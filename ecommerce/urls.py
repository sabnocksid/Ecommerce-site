from django.urls import path
from django.contrib.auth import views as auth_views
from .views import HomeView, ProductCreateView, ProductCarouselView, ProductDetailView, CategoryListView,VendorDashboardView, CategoryDetailView
from .views import signup_view, CustomLoginView, custom_logout_view, VendorLoginView, vendor_registration_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('vendor/dashboard/', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('signup/', signup_view, name='signup'),
    path('vendor/registration/', vendor_registration_view, name='vendor_registration'),
    path('vendor/login/', VendorLoginView.as_view(), name='vendor_login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('product-carousel/', ProductCarouselView.as_view(), name='product-carousel'), 
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'), 
]
