from django.urls import path
from . import views
from .views import  VendorDashboardView
from  .views import VendorLoginView, vendor_registration_view, VendorLogoutView, create_product 


urlpatterns = [
    path('', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('signup/', vendor_registration_view, name='vendor_signup'),
    path('login/', VendorLoginView.as_view(), name='vendor_login'),
    path('logout/', VendorLogoutView.as_view(), name='vendor_logout'),  
    path('products/create/', create_product, name='create_product'),  
]
