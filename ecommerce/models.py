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
    address = models.TextField(blank=True)  
    phone_number = models.CharField(max_length=15, blank=True)  

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


class Brand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)

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
    
    # Foreign key to Brand with a default value of None
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    
    colors = models.ManyToManyField(Color, blank=True)  

    def __str__(self):
        return self.name


class Offer(models.Model):
    title = models.CharField(max_length=255, help_text="Title or description of the offer")
    banner = models.ImageField(upload_to='offers/', help_text="Upload banner image (PNG recommended)")
    start_date = models.DateTimeField(null=True, blank=True, help_text="Offer start date")
    end_date = models.DateTimeField(null=True, blank=True, help_text="Offer end date")
    is_active = models.BooleanField(default=True, help_text="Check if the offer is active")

    def __str__(self):
        return self.title

    @property
    def is_current(self):
        now = timezone.now()
        if self.start_date and self.end_date:
            return self.start_date <= now <= self.end_date
        return self.is_active


class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  
    review_text = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f'Review of {self.product.name} by {self.user.username}'
