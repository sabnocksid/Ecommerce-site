from django.urls import path
from cart import views

app_name = 'cart'  # Set the namespace
urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/length/', views.cart_length, name='cart_length'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),  # This should match
]
