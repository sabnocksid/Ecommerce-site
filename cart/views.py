from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .cart import Cart
from .models import Order, OrderItem
from decimal import Decimal
from ecommerce.models import Product

PAYMENT_METHODS = [
    ('e_sewa', 'e-Sewa'),
    ('khalti', 'Khalti'),
    ('bank_transfer', 'Bank Transfer'),
    ('cash_on_delivery', 'Cash on Delivery'),
]

def calculate_totals(cart):
    subtotal = Decimal('0.00')
    discount_total = Decimal('0.00')  # Modify this based on your discount logic
    discount_percentage = Decimal('0.00')  # If you have discounts

    for item in cart.values():
        product_price = Decimal(item.get('price', '0.00'))
        quantity = Decimal(item.get('quantity', 1))
        subtotal += product_price * quantity

    total = subtotal - discount_total  # Calculate total after discount

    return {
        'subtotal': subtotal,
        'discount_total': discount_total,
        'discount_percentage': discount_percentage,
        'total': total,
    }

def add_to_cart(request, product_id):
    if request.method == "POST":
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        quantity = request.POST.get("quantity", 1)

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError("Quantity must be at least 1.")
        except ValueError:
            return JsonResponse({"error": "Invalid quantity"}, status=400)

        cart.add(product=product, quantity=quantity)

        return JsonResponse({
            "cart_qty": sum(item["quantity"] for item in cart.cart.values()),
            "message": "Product added to cart",
            "product_id": product.id,
            "product_name": product.name,
            "product_price": str(product.price),
            "product_on_sale": product.on_sale,
            "product_sale_price": str(product.sale_price) if product.on_sale else None,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

def cart_detail(request):
    cart = Cart(request)
    total = calculate_totals(cart.cart)

    context = {
        "cart": cart,
        "total": total,
    }

    return render(request, "your_cart.html", context)

def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart_detail")

def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")

def cart_length(request):
    cart = Cart(request)
    cart_qty = len(cart.cart)
    return JsonResponse({"cart_length": cart_qty})

def update_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        action = request.POST.get("action")
        quantity = int(request.POST.get("quantity", 0))

        if action == "add":
            cart.add(product, 1)  # Add one item to the cart
        elif action == "subtract":
            if quantity > 1:
                cart.add(product, -1)  # Subtract one item from the cart
            else:
                cart.remove(product)  # Remove item if quantity is 1 or less

    return redirect("cart_detail")

@login_required
def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        user = request.user
        if not cart.cart:
            messages.error(request, "Your cart is empty.")
            return redirect('cart:cart_detail')

        order = Order.objects.create(user=user)

        for item in cart:
            product = item['product']
            quantity = item['quantity']
            price = Decimal(item['price'])
            sale_price = item.get('sale_price')

            item_price = Decimal(sale_price) if sale_price and Decimal(sale_price) < price else price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item_price,
                total=item['total_price']
            )

        cart.clear()

        messages.success(request, "Your order has been placed successfully.")
        return redirect('cart:order_confirmation')

    return render(request, 'cart/checkout.html', {'cart': cart})

@login_required
def process_checkout(request):
    cart = Cart(request)

    if request.method == 'POST':
        if not cart.cart:
            messages.error(request, "Your cart is empty.")
            return redirect('cart:cart_detail')

        user = request.user
        order = Order.objects.create(user=user)

        for item in cart:
            product = item['product']
            quantity = item['quantity']
            price = Decimal(item['price'])
            sale_price = item.get('sale_price')

            item_price = Decimal(sale_price) if sale_price and Decimal(sale_price) < price else price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item_price,
                total=item['total_price']
            )

        cart.clear()

        messages.success(request, "Your order has been placed successfully. Thank you for shopping with us!")
        return redirect('orders:order_detail', order.id)

    return render(request, 'cart/checkout.html', {'cart': cart})


def order_confirmation(request):
    return render(request, 'order_confirmation.html')