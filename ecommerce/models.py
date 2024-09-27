from django.db import models
from django.contrib.auth.models import User

# TimeStampedModel for tracking creation and updates
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        abstract = True 


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    city = models.CharField(max_length=100)


    def __str__(self):
        return self.user.username

# Vendor model for sellers
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to="vendor_profile_pictures/%Y/%m/%d", blank=True, null=True)

    def __str__(self):
        return self.business_name


# Category model for product categories
class Category(TimeStampedModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Tag model for product tagging
class Tag(TimeStampedModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Product model for eCommerce products
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
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)  # Link to the Vendor model
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag)
    on_sale = models.BooleanField(default=False)

    def __str__(self):
        return self.name
