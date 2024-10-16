from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, DetailView
from .models import Product, Category, Customer, Tag, Offer, Review
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import views as auth_views
from .forms import SignupForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg
from django.http import JsonResponse
from django.core.exceptions import ValidationError



class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['offers'] = Offer.objects.filter(is_active=True, start_date__lte=timezone.now(), end_date__gte=timezone.now())
        context['sale_products'] = Product.objects.filter(on_sale=True)
        context['categories'] = Category.objects.all()
        context['latest_products'] = Product.objects.order_by('-created_at')[:5]
        context['trending_products'] = Product.objects.filter(on_sale=True).order_by('-view_count')[:5]

        # if self.request.user.is_authenticated:
        #     context['for_you_products'] = self.get_for_you_products(self.request.user)
        # else:
        #     context['for_you_products'] = None  
        return context



class ProductCarouselView(ListView):
    model = Product
    template_name = 'costumer/home/mid-section/product_carousel.html' 
    context_object_name = 'products'  
    queryset = Product.objects.order_by('-created_at')  


class ProductDetailView(DetailView):
    model = Product
    template_name = 'costumer/detail/product_detail.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        # Call the base implementation to get the object
        super().get(request, *args, **kwargs)

        product = self.object  # Get the product
        product.view_count += 1  
        product.save()

        discount_percentage = 0
        if product.on_sale and product.price and product.price > 0:
            discount_percentage = round(((product.price - product.sale_price) / product.price) * 100, 1)

        average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        reviews = product.reviews.all()

        context = self.get_context_data(object=product)
        context['discount_percentage'] = discount_percentage
        context['average_rating'] = round(average_rating, 1)  
        context['reviews'] = reviews 
        context['tags'] = product.tag.all()  

        return self.render_to_response(context)

class CategoryListView(ListView):
    model = Category
    template_name = 'costumer/home/mid-section/category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class BrandView(ListView):
    model = Product
    template_name = 'costumer/detail/brand_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        return Product.objects.filter(brand=product.brand)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        brand = product.brand
        context['brand_name'] = brand.name
        context['brand_image'] = brand.image.url if brand.image else None
        context['brand_description'] = brand.description
        return context
    


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'costumer/detail/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = self.get_object()  
        
        categories = Category.objects.all()  
        context['categories'] = categories

        context['category_products'] = Product.objects.filter(category=category)

        return context


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 

            Customer.objects.create(
                user=user,
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                phone_number=request.POST.get('phone_number', ''),
                postal_code=request.POST.get('postal_code', '')
            )
            messages.success(request, 'Account created Sucessfully please login')
            return redirect('login') 
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})



class CustomLoginView(auth_views.LoginView):
    template_name = 'login.html'

def custom_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home') 

@login_required
def add_review(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')
        
        # Basic validation
        if not product_id or not rating or not review_text:
            return JsonResponse({'success': False, 'message': 'All fields are required.'}, status=400)

        try:
            # Ensure rating is an integer and within expected range
            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({'success': False, 'message': 'Rating must be between 1 and 5.'}, status=400)

            Review.objects.create(
                user=request.user,
                product_id=product_id,
                rating=rating,
                review_text=review_text
            )
            return JsonResponse({'success': True, 'message': 'Review submitted successfully!'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error submitting review: ' + str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request.'}, status=400)
