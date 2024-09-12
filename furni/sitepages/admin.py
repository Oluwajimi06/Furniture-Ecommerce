from django.contrib import admin
from .models import Product,Blog,Cart,CartItem,Coupon,Order, OrderItem,NewsletterSubscription

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image')


# Register the Blog model with the admin site
admin.site.register(Blog)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass
                                      




# Register the Coupon model
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_amount', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    list_filter = ['is_active', 'valid_from', 'valid_to']






class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty forms to display

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'user', 
        'first_name', 
        'last_name', 
        'address',        # Shipping address
        'state_country',  # State or country
        'postal_zip',     # Postal code
        'country',        # Country
        'total_amount',
        'status',         # Display the order status 
        'created_at', 
        'updated_at'
    )
    search_fields = ('id', 'first_name', 'last_name', 'email', 'phone', 'address')
    list_filter = ('created_at', 'updated_at', 'country', 'status')

    # Enable status editing in the list view
    list_editable = ('status',)
    
    inlines = [OrderItemInline]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
    list_filter = ('order', 'product')

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subscribed_at')
    search_fields = ('name', 'email')




