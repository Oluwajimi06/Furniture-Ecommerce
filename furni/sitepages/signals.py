from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem, Product
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model






User = get_user_model()

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    session_cart = request.session.get('cart', {})
    
    if session_cart:
        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Loop through session cart and add items to the persistent cart
        for product_id, item_data in session_cart.items():
            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            
            # If the product is already in the cart, update the quantity
            if not created:
                cart_item.quantity += item_data['quantity']
            else:
                cart_item.quantity = item_data['quantity']
            
            cart_item.save()
        
        # Clear the session cart after merging
        del request.session['cart']
