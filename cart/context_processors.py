from .cart import Cart

def cart(request):
    return {'cart': Cart(request)}

def cart_length(request):
    if request.user.is_authenticated:
        cart = Cart(request)
        cart_qty = len(cart.cart)
    else:
        cart_qty = 0 

    return {"cart_length": cart_qty}