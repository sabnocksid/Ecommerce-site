from django.contrib import admin
from ecommerce.models import Category, Tag, Product, Vendor, Customer, Order

# Register your models here.
admin.site.register([Category, Tag, Product, Vendor, Customer, Order])