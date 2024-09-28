from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, DetailView
from .models import Product, Category, Customer,  Cart, CartItem, Order
from .forms import ProductForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import views as auth_views
from .forms import SignupForm
from django.contrib.auth.decorators import login_required


class HomeView(TemplateView):
    template_name = 'home.html'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['sale_products'] = Product.objects.filter(on_sale=True) 
        context['categories'] = Category.objects.all()  
        context['latest_products'] = Product.objects.order_by('-created_at')[:5] 
        context['trending_products'] = Product.objects.filter(on_sale=True).order_by('-view_count')[:5]

        return context

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('success') 


class ProductCarouselView(ListView):
    model = Product
    template_name = 'costumer/home/mid-section/product_carousel.html' 
    context_object_name = 'products'  
    queryset = Product.objects.order_by('-created_at')  


class ProductDetailView(DetailView):
    model = Product
    template_name = 'costumer/detail/product_detail.html'  # Template for product details
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
            login(request, user)  
            messages.success(request, 'Signup successful! You are now logged in.')
            return redirect('home') 
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
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = cart.items.get_or_create(product=product)
    cart_item.quantity += 1  
    cart_item.save()
    
    messages.success(request, f'{product.name} has been added to your cart.')
    return redirect('product_detail', pk=product.id) 

@login_required  
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = None  

    items = cart.items.all() if cart else [] 
    total_amount = sum(item.product.price * item.quantity for item in items)

    context = {
        'cart': cart,
        'items': items,
        'total_amount': total_amount,
    }

    if not items:
        messages.info(request, "Your cart is empty.")

    return render(request, 'view_cart.html', context)

def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.items.all()
    total_amount = sum(item.product.price * item.quantity for item in items)

    order = Order.objects.create(user=request.user, total_amount=total_amount)
    for item in items:
        item.product.stock -= item.quantity  
        item.product.save()  
    order.items.set(items)
    cart.items.all().delete()  

    messages.success(request, 'Your order has been placed successfully.')
    return render(request, 'order_confirmation.html', {'order': order})