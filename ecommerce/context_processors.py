from django.utils import timezone
from .models import Category, Vendor, Offer, Product, Brand

def global_context(request):
    context = {
        'categories': Category.objects.all(),
        'vendors': Vendor.objects.all(),
        'brands' : Brand.objects.all(),
        'offers': Offer.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ),
        'sale_products': Product.objects.filter(on_sale=True),
        'latest_products': Product.objects.order_by('-created_at')[:5],
        'trending_products': Product.objects.filter(on_sale=True).order_by('-view_count')[:5]
    }
    return context
