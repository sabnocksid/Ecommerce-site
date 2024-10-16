
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ecommerce.models import Product, Vendor  
from django_summernote.widgets import SummernoteWidget

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'availability', 'product_image',
            'price', 'sale_price', 'stock', 'category', 'tag',
            'color', 'brand', 'on_sale'
        ]
        widgets = {
            'description': SummernoteWidget(),
            'product_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'on_sale': forms.CheckboxInput(attrs={'class': 'form-check-input'})  
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter product name'})
        self.fields['availability'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['sale_price'].widget.attrs.update({'class': 'form-control'})
        self.fields['stock'].widget.attrs.update({'class': 'form-control'})
        self.fields['color'].widget.attrs.update({'class': 'form-control'})

class VendorRegistrationForm(UserCreationForm):
    business_name = forms.CharField(max_length=255, required=True)
    profile_picture = forms.ImageField(required=False)  
    phone_number = forms.CharField(max_length=15, required=True)  
    address = forms.CharField(max_length=255, required=True)  

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'business_name', 'profile_picture', 'phone_number', 'address')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()  
            Vendor.objects.create(
                user=user,
                business_name=self.cleaned_data['business_name'],
                profile_picture=self.cleaned_data.get('profile_picture', None),  
                phone_number=self.cleaned_data['phone_number'],  
                address=self.cleaned_data['address']  
            )
        return user
