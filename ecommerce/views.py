from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, DetailView
from .models import Product, Category, Customer, Tag, Offer, Review, Vendor, Brand
from cart.models import OrderItem
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import views as auth_views
from .forms import SignupForm, CustomerForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import Q, Case, When, IntegerField, Count, Sum
from cart.models import Order, OrderItem
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            customer_user = Customer.objects.filter(user=self.request.user).first()
            if customer_user:
                order_items = OrderItem.objects.filter(order__user=self.request.user).values_list('product__category', flat=True).distinct()
                if order_items.exists():
                    context['recommended_products'] = Product.objects.filter(category__in=order_items).distinct()
                else:
                    context['recommended_products'] = Product.objects.none()
            else:
                context['recommended_products'] = Product.objects.none()
        else:
            context['recommended_products'] = Product.objects.none()

        context['offers'] = Offer.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )

        sale_products = Product.objects.filter(on_sale=True)
        for product in sale_products:
            if product.sale_price and product.price:  
                discount_percentage = ((product.price - product.sale_price) / product.price) * 100
                product.discount_percentage = round(discount_percentage, 2)

        context['sale_products'] = sale_products
        context['categories'] = Category.objects.all()
        context['vendors'] = Vendor.objects.all()
        context['latest_products'] = Product.objects.order_by('-created_at')[:6]
        context['trending_products'] = Product.objects.filter(on_sale=True).order_by('-view_count')[:6]

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
        response = super().get(request, *args, **kwargs)

        product = self.object
        product.view_count += 1  
        product.save()

        discount_percentage = 0
        if product.on_sale and product.price and product.sale_price and product.price > 0:
            discount_percentage = round(((product.price - product.sale_price) / product.price) * 100, 1)

        average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        reviews = product.reviews.all()

        can_review = False
        if request.user.is_authenticated and Customer.objects.filter(pk=request.user.id).exists():
            order_items = OrderItem.objects.filter(
                order__user=request.user,
                product=product,
                order__shipment_status='Delivered'
            )
            
            has_reviewed = Review.objects.filter(
                user=request.user,
                product=product
            ).exists()
    
            if order_items.exists() and not has_reviewed:
                can_review = True

        context = self.get_context_data(object=product)
        context['discount_percentage'] = discount_percentage
        context['average_rating'] = round(average_rating, 1)
        context['reviews'] = reviews
        context['tags'] = product.tag.all()

        context['related_products'] = Product.objects.filter(
            Q(category=product.category) | Q(brand=product.brand)
        ).exclude(id=product.id)[:4]

        context['can_review'] = can_review

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
        brand_id = self.kwargs['pk']  
        return Product.objects.filter(brand__id=brand_id)  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand_id = self.kwargs['pk']
        brand = get_object_or_404(Brand, id=brand_id)  
        context['brand_name'] = brand.name
        context['brand_image'] = brand.image.url if brand.image else None
        context['brand_description'] = brand.description
        return context

class StoreView(DetailView):
    model = Vendor
    template_name = 'costumer/detail/store.html'
    context_object_name = 'vendor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        vendor = self.get_object()

        context['business_name'] = vendor.business_name
        context['profile_picture'] = vendor.profile_picture
        context['address'] = vendor.address
        context['phone_number'] = vendor.phone_number

        context['products'] = Product.objects.filter(vendor=vendor)

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

        search_query = self.request.GET.get('query', '')
        if search_query:
            context['category_products'] = context['category_products'].filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__name__icontains=search_query)  
            )
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
        
        if not product_id or not rating or not review_text:
            return JsonResponse({'success': False, 'message': 'All fields are required.'}, status=400)

        try:
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



def search_view(request):
    query = request.GET.get('query', '').strip()
    
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    sort_by = request.GET.get('sort_by', '')  # Sorting can be 'price', 'view_count', 'orders', or 'on_sale'
    on_sale = request.GET.get('on_sale', '')  # Filtering for on_sale

    products = Product.objects.all()

    if query:
        products = products.annotate(
            match_score=Case(
                When(name__iexact=query, then=3),  # Exact match in name
                When(name__icontains=query, then=2),  # Partial match in name
                When(description__icontains=query, then=1),  # Match in description
                output_field=IntegerField(),
            )
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    if on_sale == 'true':
        products = products.filter(on_sale=True)

    if sort_by == 'price':
        products = products.order_by('price')  # Ascending order by price
    elif sort_by == 'price_desc':
        products = products.order_by('-price')  # Descending order by price
    elif sort_by == 'view_count':
        products = products.order_by('-view_count')  # Descending order by view count
    elif sort_by == 'orders':
        products = products.annotate(order_count=Sum('orderitem__quantity', output_field=IntegerField())).order_by('-order_count')
    elif sort_by == 'on_sale':
        products = products.filter(on_sale=True)  # Filter products on sale
        products = products.order_by('price')  # Sort on-sale products by price

    if not sort_by:
        products = products.order_by('-match_score')

    if not sort_by:
        products = products.order_by('-match_score')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_list = [{
            'id': product.id,
            'name': product.name,
            'product_image': product.product_image.url if product.product_image else None,
            'price': product.price,
        } for product in products]

        return JsonResponse({'products': product_list})

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'on_sale': on_sale,  
    }

    return render(request, 'search_results.html', context)



@login_required
def UserProfileView(request):
    user = request.user
    try:
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        customer = None  

    context = {
        'user': user,
        'customer': customer,
    }
    return render(request, 'user_profile.html', context)



@login_required
def edit_profile(request):
    try:
        customer = request.user.customer  
    except Customer.DoesNotExist:
        customer = None

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()  
            return redirect('user-profile')  
    else:
        form = CustomerForm(instance=customer)  

    return render(request, 'edit_profile.html', {'form': form})