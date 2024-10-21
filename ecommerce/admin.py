from django.contrib import admin
from ecommerce.models import Category, Tag, Product, Vendor, Customer, Offer,Brand, Review
from cart.models import Order, OrderItem, Payment

admin.site.register([Category, Tag, Product, Vendor, Customer, Offer, Brand, Review, Order, OrderItem, Payment])