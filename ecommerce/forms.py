from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer


class SignupForm(UserCreationForm):
    address = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    postal_code = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'address', 'city', 'phone_number', 'postal_code')

    def save(self, commit=True):
        user = super().save(commit)
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                phone_number=self.cleaned_data['phone_number'],
                postal_code=self.cleaned_data['postal_code']
            )
        return user


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['address', 'city', 'phone_number', 'postal_code']