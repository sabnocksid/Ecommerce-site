from ecommerce.models import Product
from decimal import Decimal
from django.shortcuts import get_object_or_404

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)

        if product.price is None:
            raise ValueError("Product price cannot be None")

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'sale_price': str(product.sale_price) if product.sale_price is not None else None,
            }

        self.cart[product_id]['quantity'] += quantity

        if self.cart[product_id]['quantity'] <= 0:
            del self.cart[product_id]  # Remove item if quantity is 0 or less

        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.cart = {}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            price = item.get('price')
            sale_price = item.get('sale_price')
            quantity = item.get('quantity', 0)

            if sale_price and Decimal(sale_price) < Decimal(price):
                item['total_price'] = Decimal(sale_price) * quantity
            else:
                item['total_price'] = Decimal(price) * quantity

            yield item

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def get_total_price(self):
        total = Decimal('0.00')
        subtotal = Decimal('0.00')
        discount_total = Decimal('0.00')

        for item in self.cart.values():
            price = Decimal(item.get('price', '0.00'))
            sale_price = item.get('sale_price')
            quantity = item.get('quantity', 0)

            if quantity > 0:
                item_price = Decimal(sale_price) if sale_price and Decimal(sale_price) < price else price
                item_total = item_price * quantity

                subtotal += price * quantity
                total += item_total

                if sale_price and Decimal(sale_price) < price:
                    discount_total += (price - Decimal(sale_price)) * quantity

        discount_percentage = (discount_total / subtotal * 100) if subtotal > 0 else Decimal('0.00')

        return {
            'total': total,
            'subtotal': subtotal,
            'discount_total': discount_total,
            'discount_percentage': discount_percentage.quantize(Decimal('0.01'))
        }