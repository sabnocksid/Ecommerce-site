from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)    
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        abstract = True


class Customer(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username


class Vendor(TimeStampedModel):  
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to="vendor_profile_pictures/%Y/%m/%d", blank=True, null=True)

    def __str__(self):
        return self.business_name


class Category(TimeStampedModel): 
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(TimeStampedModel): 
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):  
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    availability = models.CharField(max_length=30, choices=AVAILABILITY_CHOICES, default="available")
    product_image = models.ImageField(upload_to="product_image/%Y/%m/%d", blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField()
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)  
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag)
    view_count = models.IntegerField(default=0) 
    on_sale = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(CartItem)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"