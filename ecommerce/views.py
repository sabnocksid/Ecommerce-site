from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, DetailView
from .models import Product, Category, Customer, Tag, Offer
from .forms import ProductForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import views as auth_views
from .forms import SignupForm, VendorRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

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


class VendorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor/vendor_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = Vendor.objects.get(user=self.request.user)  
        context['some_data'] = "This is additional data"
        return context


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('vendor_dashboard') 


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
        product = self.get_object()
        product.view_count += 1  
        product.save()  
        return super().get(request, *args, **kwargs)


class CategoryListView(ListView):
    model = Category
    template_name = 'costumer/home/mid-section/category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'costumer/detail/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
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

def vendor_registration_view(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'You are now a vendor, login to add your products.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VendorRegistrationForm()
    return render(request, 'vendor/vendor_registration.html', {'form': form})

class VendorLoginView(View):
    def get(self, request):
        return render(request, 'vendor/vendor_login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return render(request, 'vendor/vendor_dashboard.html')
  
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, 'vendor/vendor_login.html')


class CustomLoginView(auth_views.LoginView):
    template_name = 'login.html'

def custom_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home') 
