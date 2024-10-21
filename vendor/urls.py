from django.urls import path
from . import views
from vendor.views import  VendorDashboardView
from  vendor.views import VendorLoginView, vendor_registration_view, VendorLogoutView, create_product, add_category, add_brand, add_tag, brand_list, tag_list, category_list, vendor_orders, update_shipment_status 
app_name = 'vendor'  

urlpatterns = [
    path('', VendorDashboardView.as_view(), name='vendor_dashboard'),
    path('signup/', vendor_registration_view, name='vendor_signup'),
    path('login/', VendorLoginView.as_view(), name='vendor_login'),
    path('logout/', VendorLogoutView.as_view(), name='vendor_logout'),  
    path('products/create/', create_product, name='create_product'), 
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add-brand/', add_brand, name='add_brand'),
    path('add-category/', add_category, name='add_category'),
    path('add-tag/', add_tag, name='add_tag'),
    path('brand-list/', brand_list, name='brand_list'),
    path('category-list/', category_list, name='category_list'),
    path('tag-list/', tag_list, name='tag_list'),
    path('vendor-orders/', vendor_orders, name='vendor_orders'),
    path('update-shipment-status/<int:order_id>/', update_shipment_status, name='update_shipment_status'),


    ]
