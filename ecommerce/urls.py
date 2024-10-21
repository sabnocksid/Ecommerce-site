from django.urls import path
from django.contrib.auth import views as auth_views
from .views import HomeView, ProductCarouselView, ProductDetailView, CategoryListView,CategoryDetailView, BrandView, StoreView
from .views import signup_view, CustomLoginView, custom_logout_view, add_review, search_view
from django.urls import path, include

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('brand/<int:pk>/', BrandView.as_view(), name='brand_products'),
    path('store/<int:pk>/', StoreView.as_view(), name='store_detail'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product-carousel/', ProductCarouselView.as_view(), name='product-carousel'), 
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'), 
    path('add-review/', add_review, name='add_review'),  
    path('search/', search_view, name='search'),

]
