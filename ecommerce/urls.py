from django.urls import path
from django.contrib.auth import views as auth_views
from .views import HomeView, ProductCarouselView, ProductDetailView, CategoryListView,CategoryDetailView, BrandView, StoreView, UserProfileView
from .views import signup_view, CustomLoginView, custom_logout_view, add_review, search_view, edit_profile
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
    path('user/profile/', UserProfileView, name='user-profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),


    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
