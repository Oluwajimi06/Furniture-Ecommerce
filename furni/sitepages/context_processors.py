# context_processors.py
from .models import Coupon
from .views import cart_summary  # Adjust the import based on where your view is located
from django.utils import timezone

def cart_items_count(request):
    context = cart_summary(request)
    return context






def active_coupon_processor(request):
    now = timezone.now()
    try:
        coupon = Coupon.objects.get(is_active=True, valid_from__lte=now, valid_to__gte=now)
        return {'active_coupon': coupon}
    except Coupon.DoesNotExist:
        return {'active_coupon': None}
