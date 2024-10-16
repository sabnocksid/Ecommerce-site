from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ecommerce.models import Product, Vendor
from .forms import ProductForm, VendorRegistrationForm


# Vendor Dashboard View
class VendorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor/vendor_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the vendor name from the session
        vendor_name = self.request.session.get('vendor_name', 'Guest')
        context['vendor_name'] = vendor_name
        # Get the vendor object for the logged-in user
        context['vendor'] = Vendor.objects.get(user=self.request.user)
        context['some_data'] = "This is additional data"
        return context


def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor  # Assuming you have a vendor relationship
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('vendor_dashboard')
        else:
            print(form.errors)  # Check the errors in the console
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {'form': form}) 



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
            vendor = Vendor.objects.get(user=user)
            request.session['vendor_name'] = vendor.business_name
            messages.success(request, 'Logged in successfully!')
            return redirect('vendor_dashboard')  
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, 'vendor/vendor_login.html')


class VendorLogoutView(View):
    def get(self, request):
        logout(request)  # Logs the user out
        messages.success(request, 'You have logged out successfully.')
        return redirect('vendor_login') 