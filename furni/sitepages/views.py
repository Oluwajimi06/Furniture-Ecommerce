from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse 
from django.contrib import messages
from .models import Product,Blog,CartItem,Cart,Coupon,Order, OrderItem,NewsletterSubscription
from django.utils import timezone
from decimal import Decimal
from django.contrib.sessions.models import Session
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags




def Home(request):
    # Check if the cart is already in session, if not, initialize an empty cart
    if 'cart' not in request.session:
        request.session['cart'] = {}

    # Handle authenticated users with a cart
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
    else:
        cart_items = []

    # Fetch all products from the database
    products = Product.objects.all()
    
    # Fetch the 3 most recent published blog posts
    recent_blogs = Blog.objects.filter(is_published=True).order_by('-published_date')[:3]

    data = {
        'ptitle': 'Furni - Home',
        'products': products,  # Pass the products to the template
        'recent_blogs': recent_blogs,
        'cart_items': cart_items,  # Pass cart items to the template
    }
    
    return render(request, 'sitepages/index.html', data)






def Shop(request):
    products = Product.objects.all()  # Fetch all products from the database
    
    data = {
        'ptitle': 'Furni - Shop',
        'products': products,
    }
    return render(request, 'sitepages/shop.html', data)




def About(request):
    # Fetch all products from the database
    products = Product.objects.all()
   
    
    data = {
        'ptitle': 'Furni - About',
        'products': products,
    }
    return render(request, 'sitepages/about.html', data)


def Service(request):
    products = Product.objects.all()
    
    
    data = {
        'ptitle': 'Furni - Services',
        'products': products,
    }
    return render(request, 'sitepages/services.html', data)






def Blog_list(request):
    products = Product.objects.all()
    
    blogs = Blog.objects.all().order_by('-published_date')  # Fetch all blogs ordered by the most recent first
    
    data = {
        'ptitle': 'Furni - Blogs',
        'blogs': blogs,
        'products': products,
    }
    return render(request, 'sitepages/blog.html', data)





def blog_detail(request, pk):
    products = Product.objects.all()
    blog = get_object_or_404(Blog, pk=pk)
    
    return render(request, 'sitepages/blog_detail.html', {
        'blog': blog,
        'products': products,
    })



def Contact(request):
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(first_name)


        send_mail(
            f"Contact Form Submission from {first_name} {last_name}",
            f"Message: {message}\n\nFrom: {first_name} {last_name}, Email: {email}",
            email,  # From email
            ['admin@example.com'],  # Admin email to receive the message
        )

        messages.success(request, 'Your message has been sent successfully!')


    products = Product.objects.all()
    data = {
        'ptitle': 'Furni - Contact',
        'products': products,
    }
    return render(request, 'sitepages/contact.html', data)





def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sitepages/product_detail.html', {
        'product': product,
    })




def cart_detail(request):
    # Initialize cart items and total
    cart_items = []
    cart_total = Decimal(0)

    # Check if the user is authenticated
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        for item in cart.items.all():
            cart_items.append({
                'product': item.product,
                'name': item.product.name,
                'price': item.product.price,
                'quantity': item.quantity,
                'total_price': item.get_total_price(),
                'image': item.product.image.url if item.product.image else None
            })
            cart_total += item.get_total_price()
    else:
        # Handle guest user's session-based cart
        session_cart = request.session.get('cart', {})
        for product_id, details in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total_price = Decimal(details['price']) * details['quantity']
                cart_items.append({
                    'product': product,
                    'name': details['name'],
                    'price': details['price'],
                    'quantity': details['quantity'],
                    'total_price': total_price,
                    'image': details['image'],
                })
                cart_total += total_price
            except Product.DoesNotExist:
                continue  # Skip if product does not exist

    # Store the total amount in the session if proceeding to checkout
    if 'proceed_to_checkout' in request.POST:
        request.session['cart_total'] = str(cart_total)
        return redirect('sitepages:checkoutpage')

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'ptitle' : 'Furni - Cart'
    }

    return render(request, 'sitepages/cart.html', context)





def update_cart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            for key, value in request.POST.items():
                if key.startswith('quantity_'):
                    product_id = key.split('_')[1]
                    quantity = int(value)
                    product = get_object_or_404(Product, id=product_id)
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                    if quantity <= 0:
                        cart_item.delete()
                    else:
                        cart_item.quantity = quantity
                        cart_item.save()
        else:
            # Handle the session cart logic here
            cart = request.session.get('cart', {})
            for key, value in request.POST.items():
                if key.startswith('quantity_'):
                    product_id = key.split('_')[1]
                    quantity = int(value)
                    if quantity <= 0:
                        if product_id in cart:
                            del cart[product_id]
                    else:
                        # Fetch product to get the latest price
                        try:
                            product = Product.objects.get(id=product_id)
                            cart[product_id] = {
                                'quantity': quantity,
                                'price': str(product.price),  # Convert price to string for storage
                                'name': product.name,
                                'image': product.image.url,
                            }
                        except Product.DoesNotExist:
                            continue  # Skip if product does not exist
            request.session['cart'] = cart
        
        return redirect('sitepages:cartpage')






def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        # Handle cart for logged-in users
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Add or update the CartItem for the product
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
    
    else:
        # Handle session-based cart for guest users
        cart = request.session.get('cart', {})
        
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {
                'name': product.name,
                'price': str(product.price),
                'quantity': 1,
                'image': str(product.image.url)
            }
        
        # Save the cart back to the session
        request.session['cart'] = cart
    
    # Add a success message
    messages.success(request, f"{product.name} has been added to your cart.")
    
    return redirect('sitepages:shoppage')  # Redirect to the cart details page






def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        # Handle cart for logged-in users
        cart = Cart.objects.get(user=request.user)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass  # If the item is not in the cart, do nothing

    else:
        # Handle session-based cart for guest users
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
    
    return redirect('sitepages:cartpage')  # Redirect to the cart details page



def cart_summary(request):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        total_items = cart.items.count()
    else:
        cart = request.session.get('cart', {})
        total_items = sum(details['quantity'] for details in cart.values())

    return {
        'total_items': total_items,
    }







def Checkout(request):
    cart_items = []
    cart_subtotal = Decimal(0)
    coupon_discount = Decimal(0)
    applied_coupon = None

    # Handle shipping form data (if submitted)
    if request.method == 'POST':
        if 'place_order' in request.POST:
            # Save the shipping data in the session before placing the order
            shipping_data = request.session.get('shipping_data', {})
            shipping_data.update({
                'country': request.POST.get('c_country'),
                'first_name': request.POST.get('c_fname'),
                'last_name': request.POST.get('c_lname'),
                'address': request.POST.get('c_address'),
                'state_country': request.POST.get('c_state_country'),
                'postal_zip': request.POST.get('c_postal_zip'),
                'email': request.POST.get('c_email_address'),
                'phone': request.POST.get('c_phone'),
            })
            request.session['shipping_data'] = shipping_data
            print("Shipping data saved in session:", shipping_data)  # Debugging line
            messages.success(request, 'Shipping information saved successfully!')
            
            # Save cart total and coupon discount
            cart_total = request.session.get('cart_total', 0) / 100
            coupon_discount = request.session.get('coupon_discount', 0) / 100

            context = {
                'cart_total': cart_total,
                'coupon_discount': coupon_discount,
                'shipping_data': shipping_data,
            }
            
            # Render confirmation page directly if data is saved
            return render(request, 'sitepages/confirmation.html', context)

        elif 'coupon_code' in request.POST:
            coupon_code = request.POST.get('coupon_code', '').strip()
            try:
                now = timezone.now()
                coupon = Coupon.objects.get(
                    code=coupon_code,
                    is_active=True,
                    valid_from__lte=now,
                    valid_to__gte=now
                )
                coupon_discount = coupon.discount_amount
                applied_coupon = coupon
                messages.success(request, f"Coupon '{coupon_code}' applied successfully!")
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid or expired coupon code.')

    # Calculate cart subtotal
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            for item in cart.items.all():
                item_total_price = item.get_total_price()
                cart_items.append({
                    'product': item.product,
                    'name': item.product.name,
                    'price': item.product.price,
                    'quantity': item.quantity,
                    'total_price': item_total_price,
                    'image': item.product.image.url if item.product.image else None
                })
                cart_subtotal += item_total_price
        except Cart.DoesNotExist:
            pass
    else:
        session_cart = request.session.get('cart', {})
        for product_id, details in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total_price = Decimal(details['price']) * details['quantity']
                cart_items.append({
                    'product': product,
                    'name': details['name'],
                    'price': details['price'],
                    'quantity': details['quantity'],
                    'total_price': total_price,
                    'image': details['image'],
                })
                cart_subtotal += total_price
            except Product.DoesNotExist:
                continue

    # Apply discount
    cart_total = cart_subtotal - coupon_discount
    cart_total = max(cart_total, Decimal(0))  # Ensure the total does not go below zero

    # Save coupon and cart total in the session
    request.session['cart_total'] = int(cart_total * 100)  # Convert to cents for Stripe
    request.session['coupon_discount'] = int(coupon_discount * 100)  # Store coupon discount

    # Redirect to confirmation page or render checkout page
    if request.method == 'POST' and 'place_order' in request.POST:
        # The data is already saved in the session, just redirect to confirmation page
        return redirect('sitepages:confirmation')

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'coupon_discount': coupon_discount,
        'cart_total': cart_total,
        'applied_coupon': applied_coupon,
        'ptitle' : 'Furni - Checkout'
    }

    return render(request, 'sitepages/checkout.html', context)




def ConfirmationView(request):
    cart_total = request.session.get('cart_total', 0) / 100  # Convert cents to dollars
    coupon_discount = request.session.get('coupon_discount', 0) / 100  # Convert cents to dollars
    shipping_data = request.session.get('shipping_data', {})

    if cart_total == 0:
        messages.error(request, 'No cart total available.')
        return redirect('sitepages:checkout')

    context = {
        'cart_total': cart_total,
        'coupon_discount': coupon_discount,
        'shipping_data': shipping_data,
    }

    return render(request, 'sitepages/confirmation.html', context)





# stripe.api_key = settings.STRIPE_SECRET_KEY
@csrf_exempt
def StripePaymentView(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    cart_total = request.session.get('cart_total', 0)
    print(f"Stripe unit_amount (in cents): {cart_total}")
    
    if cart_total == 0:
        # Handle error - no cart total available
        messages.error(request, 'No cart total available.')
        return redirect('sitepages:checkout')

    try:
        # Initialize a Stripe session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Your Cart Items',
                        },
                        'unit_amount': int(cart_total),  # Stripe expects amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )
    except stripe.error.CardError as e:
        # Handle card errors (e.g., card declined)
        messages.error(request, f'Payment failed: {e.user_message}')
        return redirect('sitepages:checkoutpage')
    except stripe.error.RateLimitError as e:
        # Handle rate limit errors
        messages.error(request, 'Rate limit error. Please try again later.')
        return redirect('sitepages:checkoutpage')
    except stripe.error.InvalidRequestError as e:
        # Handle invalid request errors
        messages.error(request, 'Invalid request. Please try again.')
        return redirect('sitepages:checkoutpage')
    except stripe.error.AuthenticationError as e:
        # Handle authentication errors
        messages.error(request, 'Authentication error. Please try again.')
        return redirect('sitepages:checkoutpage')
    except stripe.error.APIConnectionError as e:
        # Handle API connection errors
        messages.error(request, 'Network error. Please try again.')
        return redirect('sitepages:checkoutpage')
    except stripe.error.StripeError as e:
        # Handle any other Stripe errors
        messages.error(request, 'Something went wrong. Please try again.')
        return redirect('sitepages:checkoutpage')
    except Exception as e:
        # Handle any non-Stripe errors
        messages.error(request, 'An unexpected error occurred. Please try again.')
        return redirect('sitepages:checkoutpage')

    return redirect(session.url, code=303)







def PaymentSuccessView(request):
    # Retrieve the cart total and other details from the session
    cart_total = request.session.get('cart_total', 0) / 100  # Convert cents to dollars
    coupon_discount = request.session.get('coupon_discount', 0) / 100
    shipping_data = request.session.get('shipping_data', {})

    if cart_total == 0:
        messages.error(request, 'No cart total available.')
        return redirect('/')

    # Get or create the user if authenticated
    user = request.user if request.user.is_authenticated else None

    # Create the order
    order = Order.objects.create(
        user=user,
        first_name=shipping_data.get('first_name'),
        last_name=shipping_data.get('last_name'),
        address=shipping_data.get('address'),
        state_country=shipping_data.get('state_country'),
        postal_zip=shipping_data.get('postal_zip'),
        email=shipping_data.get('email'),
        phone=shipping_data.get('phone'),
        country=shipping_data.get('country'),
        total_amount=cart_total,
        coupon_discount=coupon_discount,
        status='pending',  # Setting the initial status
    )

    # Save the order items
    order_items = []  # Collect order items to display in the email
    if user:
        try:
            cart = Cart.objects.get(user=user)
            for item in cart.items.all():
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                order_items.append(order_item)
            # Clear the cart
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass
    else:
        session_cart = request.session.get('cart', {})
        for product_id, details in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=details['quantity'],
                    price=product.price
                )
                order_items.append(order_item)
            except Product.DoesNotExist:
                continue
        # Clear the cart from session
        request.session.pop('cart', None)

    # Send a confirmation email to the user
    if shipping_data.get('email'):
        subject = 'Order Confirmation'
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'order_items': order_items,
            'shipping_data': shipping_data,
            'total_amount': order.total_amount, 
        })
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to = shipping_data.get('email')

        send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    # Send a notification email to the shop owner
    shop_owner_email = settings.EMAIL_HOST_USER  # Replace with the actual shop owner's email
    owner_subject = 'New Order Received'
    
    # Create a message that lists the ordered products
    product_list = "\n".join([f"{item.quantity}x {item.product.name}" for item in order_items])
    
    owner_message = f"""
    A new order has been placed by {shipping_data.get('first_name')} {shipping_data.get('last_name')}:
    
    Order Details:
    {product_list}
    
    Total Amount: ${order.total_amount}
    """
    
    send_mail(owner_subject, owner_message, from_email, [shop_owner_email])

    # Clear session data
    request.session.pop('cart_total', None)
    request.session.pop('coupon_discount', None)
    request.session.pop('shipping_data', None)

    # Notify user of successful payment
    messages.success(request, 'Payment was successful! Your order has been placed and a confirmation email has been sent.')

    # Render the success page
    return render(request, 'sitepages/payment_success.html')



def PaymentCancelView(request):
    # Handle cancelled payment
    # Notify the user that the payment was cancelled
    messages.error(request, 'Payment was cancelled. Please try again or contact support if you need help.')

    return render(request, 'sitepages/payment_cancel.html')





@login_required
def OrderHistoryView(request):
    # Fetch the orders of the authenticated user
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Order by most recent first

    context = {
        'orders': user_orders,
        'ptitle' : 'Furni - Order History'
    }

    return render(request, 'sitepages/order_history.html', context)





@login_required
def OrderDetailView(request, order_id):
    # Get the specific order by ID
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()  

    context = {
        'order': order,
        'order_items': order_items,
        'ptitle' : 'Furni - Order Details'
    }

    return render(request, 'sitepages/order_detail.html', context)



def newsletter_signup(request):
    if request.method == 'POST':
        # Get the data from the form submission
        name = request.POST.get('name')
        email = request.POST.get('email')

        # Validate and save to the database
        if name and email:
            # Check if the email already exists in the database
            if NewsletterSubscription.objects.filter(email=email).exists():
                messages.error(request, 'This email is already subscribed to the newsletter.')
            else:
                # Save the new subscriber
                NewsletterSubscription.objects.create(name=name, email=email)
                
                # Send a confirmation email to the subscriber
                subject = 'Thank You for Subscribing to Our Newsletter!'
                message = f"Hi {name},\n\nThank you for subscribing to our newsletter. We're excited to share our latest updates with you."
                from_email = settings.EMAIL_HOST_USER  # Use your email here
                recipient_list = [email]
                
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                messages.success(request, 'You have successfully subscribed to the newsletter! A confirmation email has been sent.')
        else:
            messages.error(request, 'Please provide both your name and email.')

    # Redirect back to the same page
    return redirect(request.META.get('HTTP_REFERER', 'sitepages:homepage'))








# correct one presently before stripe stuff
# def Checkout(request):
#     cart_items = []
#     cart_subtotal = Decimal(0)  # Initialize cart subtotal
#     coupon_discount = Decimal(0)
#     applied_coupon = None
    
#     # Check if a coupon code has been submitted
#     if request.method == 'POST' and 'coupon_code' in request.POST:
#         coupon_code = request.POST.get('coupon_code', '').strip()
#         try:
#             # Find the coupon and check if it's active and within the valid period
#             now = timezone.now()  # Get the current time as a timezone-aware object
#             coupon = Coupon.objects.get(
#                 code=coupon_code,
#                 is_active=True,
#                 valid_from__lte=now,
#                 valid_to__gte=now
#             )
#             coupon_discount = coupon.discount_amount
#             applied_coupon = coupon
#             messages.success(request, f"Coupon '{coupon_code}' applied successfully! You get a discount of ${coupon_discount}.")
#         except Coupon.DoesNotExist:
#             messages.error(request, 'Invalid or expired coupon code.')

#     # Calculate cart subtotal and total based on whether a coupon is applied
#     if request.user.is_authenticated:
#         try:
#             cart = Cart.objects.get(user=request.user)
#             for item in cart.items.all():
#                 item_total_price = item.get_total_price()
#                 cart_items.append({
#                     'product': item.product,
#                     'name': item.product.name,
#                     'price': item.product.price,
#                     'quantity': item.quantity,
#                     'total_price': item_total_price,
#                     'image': item.product.image.url if item.product.image else None
#                 })
#                 cart_subtotal += item_total_price  # Update cart subtotal
#         except Cart.DoesNotExist:
#             pass
#     else:
#         # Handle guest user's session-based cart
#         session_cart = request.session.get('cart', {})
#         for product_id, details in session_cart.items():
#             try:
#                 product = Product.objects.get(id=product_id)
#                 total_price = Decimal(details['price']) * details['quantity']
#                 cart_items.append({
#                     'product': product,
#                     'name': details['name'],
#                     'price': details['price'],
#                     'quantity': details['quantity'],
#                     'total_price': total_price,
#                     'image': details['image'],
#                 })
#                 cart_subtotal += total_price  # Update cart subtotal
#             except Product.DoesNotExist:
#                 continue  # Skip if product does not exist

#     # Adjust the cart total based on the coupon discount
#     cart_total = cart_subtotal - coupon_discount
#     cart_total = max(cart_total, Decimal(0))  # Ensure cart total doesn't go below zero

#     context = {
#         'cart_items': cart_items,
#         'cart_subtotal': cart_subtotal,
#         'coupon_discount': coupon_discount,
#         'cart_total': cart_total,
#         'applied_coupon': applied_coupon,
#     }

#     return render(request, 'sitepages/checkout.html', context)
