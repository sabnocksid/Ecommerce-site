from django.shortcuts import render, get_object_or_404
from .cart import Cart
from ecommerce.models import Product
from django.http import JsonResponse

def cart_summary(request):
    return render(request, "your_cart.html", {})

def cart_add(request):
    cart = Cart(request)

    # Corrected 'POST' to uppercase
    if request.POST.get('action') == 'post':
        # Safely convert the product_id to an integer
        product_id = int(request.POST.get('product_id'))

        # Fetch the product using get_object_or_404
        product = get_object_or_404(Product, id=product_id)

        # Add the product to the cart
        cart.add(product=product)

        # Return the product name in a JsonResponse
        response = JsonResponse({'product_name': product.name})
        return response

def cart_delete(request):
    pass

def cart_update(request):
    pass
