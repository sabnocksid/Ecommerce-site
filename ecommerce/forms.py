from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Customer

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description','availability','product_image','price','sale_price','stock','category','tag','vendor','on_sale']


class SignupForm(UserCreationForm):
    address = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    postal_code = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'address', 'city', 'phone_number', 'postal_code')

    def save(self, commit=True):
        user = super().save(commit)
        if commit:
            user.save()
            Customer.objects.create(user=user, address=self.cleaned_data['address'], city=self.cleaned_data['city'], phone_number=self.cleaned_data['phone_number'], postal_code=self.cleaned_data['postal_code'])
        return user