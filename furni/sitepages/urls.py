from django.urls import path
from .views import *

app_name="sitepages"
# Create your views here.
urlpatterns = [
    path('',Home,name="homepage"),
    path('shop/',Shop,name="shoppage"),
    path('about/',About,name="aboutpage"),
    path('services/',Service,name="servicepage"),
    path('blogs/',Blog_list,name="blogpage"),
    path('contact/',Contact,name="contactpage"),
    path('cart/',cart_detail,name="cartpage"),
    path('checkout/',Checkout,name="checkoutpage"),
    path('stripe/payment/', StripePaymentView, name='stripe_payment'),
    path('confirmation/', ConfirmationView, name='confirmation'),
    path('success/', PaymentSuccessView, name='payment_success'),
    path('cancel/', PaymentCancelView, name='payment_cancel'),
    path('product/<int:pk>/',product_detail, name='product_detail'),
    path('blog-details/<int:pk>/',blog_detail, name='detail'),  # Blog detail URL

    path('add-to-cart/<int:product_id>/',add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/',remove_from_cart, name='remove_from_cart'),  # Remove from cart
    path('update-cart/',update_cart, name='update_cart'),

    path('order-history/',OrderHistoryView, name='order_history'),
    path('order/<int:order_id>/',OrderDetailView, name='order_detail'),
    path('newsletter/signup/', newsletter_signup, name='newsletter_signup'), 
]

