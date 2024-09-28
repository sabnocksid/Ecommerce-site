from django.urls import path
from django.contrib.auth import views as auth_views
from .views import HomeView, ProductCreateView, ProductCarouselView, ProductDetailView, CategoryListView, CategoryDetailView, add_to_cart, view_cart, checkout
from .views import signup_view, CustomLoginView, custom_logout_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('product-carousel/', ProductCarouselView.as_view(), name='product-carousel'), 
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'), 
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('user_cart/', view_cart, name='user_cart'), 
    path('checkout/', checkout, name='checkout'),
]
