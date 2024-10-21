from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages
from ecommerce.models import Product
from .models import Order, OrderItem, Payment
from .cart import Cart
import logging



def calculate_totals(cart):
    subtotal = Decimal('0.00')
    discount_total = Decimal('0.00')
    discount_percentage = Decimal('0.00')

    for item in cart.values():
        product_price = Decimal(item.get('price', '0.00'))
        quantity = Decimal(item.get('quantity', 1))
        subtotal += product_price * quantity

        if item.get('sale_price') and Decimal(item['sale_price']) < product_price:
            discount_total += (product_price - Decimal(item['sale_price'])) * quantity

    if subtotal > 0:
        discount_percentage = (discount_total / subtotal) * 100 
        discount_percentage = round(discount_percentage, 2)

    total = subtotal - discount_total
    return {
        'subtotal': subtotal,
        'discount_total': discount_total,
        'discount_percentage': discount_percentage,
        'total': total,
    }

@login_required
def cart_detail(request):
    cart = Cart(request)
    total = calculate_totals(cart.cart)

    context = {
        "cart": cart,
        "total": total,
    }

    return render(request, "your_cart.html", context)

@login_required
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

@login_required
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')  # Use the correct namespaced URL

@login_required
def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart:cart_detail')  # Use the correct namespaced URL

@login_required
def cart_length(request):
    cart = Cart(request)
    cart_qty = len(cart.cart)
    return JsonResponse({"cart_length": cart_qty})

@login_required
def update_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        action = request.POST.get("action")
        quantity = int(request.POST.get("quantity", 0))

        if action == "add":
            cart.add(product, 1)
        elif action == "subtract":
            if quantity > 1:
                cart.add(product, -1)
            else:
                cart.remove(product)

    return redirect('cart:cart_detail')  

@login_required
def create_order(request):
    cart = Cart(request) 

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method')

        total_price_data = cart.get_total_price()  
        total_amount = total_price_data['total']

        if shipping_address:  
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                shipping_address=shipping_address,
                payment_method=payment_method,
                payment_status='Pending'  # Set initial status
            )
            
            for item in cart:
                product = item['product']
                quantity = item['quantity']
                price = item['price']
                total_price = item['total_price']

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    total_price=total_price
                )

                product.stock -= quantity  
                product.save()  

            Payment.objects.create(
                order=order,
                user=request.user,
                payment_method=payment_method,
                payment_status='Pending'  # Set initial status
            )
            
            cart.clear()  

            return redirect('cart:order_confirmation', order_id=order.id)
        else:
            messages.error(request, "Shipping address is required.")
    
    return render(request, 'checkout.html', {
        'cart': cart,
        'total_price': cart.get_total_price()
    })




@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})


@login_required
def order_detail(request):
    orders = Order.objects.filter(user=request.user)

    return render(request, 'order_detail.html', {'orders': orders})

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail_view.html', {'order': order})