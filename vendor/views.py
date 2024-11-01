from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, TemplateView, DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from ecommerce.models import Product, Vendor, Category, Tag, Brand, Customer
from cart.models import Order, OrderItem
from .forms import ProductForm, VendorRegistrationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q, Avg, Value
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.utils import timezone


class VendorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor/vendor_dashboard.html'
    login_url = 'vendor:vendor_login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            vendor = Vendor.objects.get(user=self.request.user)
            context['vendor'] = vendor
            context['vendor_name'] = vendor.business_name
            your_product = Product.objects.filter(vendor=vendor).annotate(
                total_sales=Sum(
                    'orderitem__quantity',
                    filter=Q(orderitem__order__shipment_status='Delivered'),  
                    default=0
                ),
                total_orders=Sum(
                    'orderitem__quantity',
                    filter=Q(orderitem__order__shipment_status__in=['Delivered', 'Pending', 'Canceled']), 
                    default=0
                ),
                total_items=F('stock') + Sum('orderitem__quantity', default=0),
                average_rating=Coalesce(Avg('reviews__rating'), Value(0.0))
            ).order_by('-created_at')
            context['your_product'] = your_product
            context['brand_list'] = Brand.objects.all()
            context['category_list'] = Category.objects.all()
            context['tag_list'] = Tag.objects.all()
            now = timezone.now()
            top_selling_products = (
                OrderItem.objects.filter(
                    product__vendor=vendor,
                    order__shipment_status='Delivered'
                )
                .values('product', 'product__name')
                .annotate(total_sales=Sum('quantity'))
                .order_by('-total_sales')[:5]
            )

            highest_ordered_products = (
                OrderItem.objects.filter(product__vendor=vendor)
                .values('product', 'product__name')
                .annotate(order_count=Count('order'))
                .order_by('-order_count')[:5]
            )

            most_viewed_products = (
                Product.objects.filter(vendor=vendor)
                .order_by('-view_count')[:5]
            )

            most_reviewed_products = (
                Product.objects.filter(vendor=vendor)
                .annotate(review_count=Count('reviews'))
                .order_by('-review_count')[:5]
            )
            overall_rating = Product.objects.filter(vendor=vendor).aggregate(Avg('reviews__rating'))['reviews__rating__avg'] or 0.0
            total_order_times = OrderItem.objects.filter(product__vendor=vendor).count()
            total_orders = OrderItem.objects.filter(product__vendor=vendor).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
            total_customers = OrderItem.objects.filter(product__vendor=vendor).values('order__user').distinct().count()  
            total_visits = Product.objects.filter(vendor=vendor).aggregate(total_view_count=Sum('view_count'))['total_view_count'] or 0

            total_items_sold = (
                OrderItem.objects.filter(
                    product__vendor=vendor,
                    order__shipment_status='Delivered'
                )
                .aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
            )

            total_earnings = (
                OrderItem.objects.filter(
                    product__vendor=vendor,
                    order__shipment_status='Delivered'
                )
                .aggregate(total_earnings=Sum('total_price'))['total_earnings'] or 0.0
            )

            context.update({
                'top_selling_products': top_selling_products,
                'highest_ordered_products': highest_ordered_products,
                'most_viewed_products': most_viewed_products,
                'most_reviewed_products': most_reviewed_products,
                'total_items_sold': total_items_sold,
                'total_earnings': total_earnings,
                'total_orders': total_orders,  # Total orders
                'total_order_times': total_order_times,  # Total orders
                'total_customers': total_customers,  # Total unique customers
                'total_visits': total_visits,  # Total visits across products
                'overall_rating': overall_rating,
            })

        except Vendor.DoesNotExist:
            raise PermissionDenied

        return context


def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor  
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('vendor_dashboard')
        else:
            print(form.errors)  
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {'form': form}) 


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('/vendor')  
    else:
        form = ProductForm(instance=product)

    return render(request, 'vendor/edit_product.html', {'form': form, 'product': product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.delete()
        return redirect('/vendor') 

    return render(request, 'vendor/delete_product.html', {'product': product})

@csrf_exempt
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')

        if name:
            category = Category.objects.create(name=name)  
            return JsonResponse({'status': 'success', 'category_id': category.id})
        else:
            return JsonResponse({'status': 'error', 'message': 'Name is required.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def add_brand(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        description = request.POST.get('description')

        brand = Brand(name=name, image=image, description=description)
        brand.save()

        return redirect('/')  

    return render(request, 'add_brand.html') 

@csrf_exempt  
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Category.objects.create(name=name)
        return JsonResponse({'message': 'Category added successfully!'})
    return JsonResponse({'error': 'Error adding category'}, status=400)

@csrf_exempt 
def add_tag(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Tag.objects.create(name=name)
        return JsonResponse({'message': 'Tag added successfully!'})
    return JsonResponse({'error': 'Error adding tag'}, status=400)

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


def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'vendor/brand_list.html', {'brands': brands})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'vendor/category_list.html', {'categories': categories})

def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'vendor/tag_list.html', {'tags': tags})

class VendorLoginView(View):
    def get(self, request):
        return render(request, 'vendor/vendor_login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            vendor = Vendor.objects.get(user=user)
            request.session['vendor_name'] = vendor.business_name
            messages.success(request, 'Logged in successfully!')
            return redirect('/vendor')  
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, 'vendor/vendor_login.html')


class VendorLogoutView(View):
    def get(self, request):
        logout(request)  
        messages.success(request, 'You have logged out successfully.')
        return redirect('vendor_login') 


@login_required
def vendor_orders(request):
    vendor = request.user.vendor
    orders = Order.objects.filter(items__product__vendor=vendor).distinct().order_by('-created_at')
    return render(request, 'vendor/vendor_orders.html', {'orders': orders})

@login_required
def update_shipment_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        shipment_status = request.POST.get('shipment_status')
        if shipment_status:
            order.shipment_status = shipment_status
            order.save()
        return redirect('vendor:vendor_orders')