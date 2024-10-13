from django.contrib import admin
from ecommerce.models import Category, Tag, Product, Vendor, Customer, Offer

# Register your models here.
admin.site.register([Category, Tag, Product, Vendor, Customer, Offer])