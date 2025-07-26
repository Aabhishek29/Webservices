from django.contrib import admin
from .models import Cart, Order, TransactionModel, OrderItem, Wishlist

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderId', 'user', 'shippingAddress', 'trackingId')
    search_fields = ('user__email', 'productId__productName', 'trackingId')
    list_filter = ('shippingAddress',)
    inlines = [OrderItemInline]  # Show order items inline

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cartId', 'user', 'product', 'createdAt', 'updatedAt')
    search_fields = ('user__email', 'product__productName')
    list_filter = ('createdAt',)

@admin.register(TransactionModel)
class TransactionModelAdmin(admin.ModelAdmin):
    list_display = ('transactionId',)
    search_fields = ('transactionId',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__orderId', 'product__productName')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__firstName', 'product__productName')
    list_filter = ('added_at',)