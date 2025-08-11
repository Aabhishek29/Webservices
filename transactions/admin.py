from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Cart, CartItem, Wishlist, Order, OrderItem,
    Transaction, OrderStatusHistory
)


# ============ INLINE ADMIN CLASSES ============

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price', 'addedAt', 'updatedAt']
    fields = ['product', 'quantity', 'total_price', 'addedAt']

    def total_price(self, obj):
        if obj.pk:
            return f"₹{obj.total_price}"
        return "-"

    total_price.short_description = "Total Price"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['totalPrice', 'productName', 'productSku']
    fields = ['product', 'productName', 'quantity', 'unitPrice', 'totalPrice']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['createdAt']
    fields = ['status', 'notes', 'createdBy', 'createdAt']


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ['transactionId', 'status', 'createdAt', 'completedAt']
    fields = ['transactionId', 'status', 'amount', 'razorpay_payment_id', 'createdAt']


# ============ ADMIN CLASSES ============

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cartId', 'user', 'items_count', 'total_amount', 'isActive', 'createdAt']
    list_filter = ['isActive', 'createdAt', 'updatedAt']
    search_fields = ['user__email', 'user__firstName', 'user__lastName']
    readonly_fields = ['cartId', 'total_items', 'total_amount', 'createdAt', 'updatedAt']
    inlines = [CartItemInline]

    def items_count(self, obj):
        return obj.items_count

    items_count.short_description = "Items Count"

    def total_amount(self, obj):
        return f"₹{obj.total_amount}"

    total_amount.short_description = "Total Amount"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart_user', 'product', 'quantity', 'unit_price', 'total_price', 'addedAt']
    list_filter = ['addedAt', 'updatedAt']
    search_fields = ['cart__user__email', 'product__name']
    readonly_fields = ['total_price', 'unit_price', 'addedAt', 'updatedAt']

    def cart_user(self, obj):
        return obj.cart.user

    cart_user.short_description = "User"

    def unit_price(self, obj):
        return f"₹{obj.unit_price}"

    unit_price.short_description = "Unit Price"

    def total_price(self, obj):
        return f"₹{obj.total_price}"

    total_price.short_description = "Total Price"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cart__user', 'product')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['wishlistId', 'user', 'product', 'product_price', 'createdAt']
    list_filter = ['createdAt']
    search_fields = ['user__email', 'user__firstName', 'product__name']
    readonly_fields = ['wishlistId', 'product_price', 'createdAt']

    def product_price(self, obj):
        return f"₹{obj.product.price}"

    product_price.short_description = "Product Price"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'orderNumber', 'user', 'status', 'paymentStatus',
        'total_items', 'totalAmount', 'createdAt'
    ]
    list_filter = [
        'status', 'paymentStatus', 'createdAt', 'isGift'
    ]
    search_fields = [
        'orderNumber', 'user__email', 'user__firstName',
        'trackingId', 'razorpay_order_id'
    ]
    readonly_fields = [
        'orderId', 'orderNumber', 'total_items', 'createdAt',
        'updatedAt', 'view_user', 'view_addresses'
    ]
    inlines = [OrderItemInline, OrderStatusHistoryInline, TransactionInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('orderId', 'orderNumber', 'view_user', 'status', 'paymentStatus')
        }),
        ('Addresses', {
            'fields': ('view_addresses',)
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'taxAmount', 'shippingAmount', 'discountAmount', 'totalAmount')
        }),
        ('Shipping & Payment', {
            'fields': ('trackingId', 'razorpay_order_id')
        }),
        ('Additional Information', {
            'fields': ('notes', 'isGift', 'giftMessage')
        }),
        ('Timestamps', {
            'fields': ('createdAt', 'updatedAt', 'deliveredAt')
        })
    )

    def total_items(self, obj):
        return obj.total_items

    total_items.short_description = "Total Items"

    def view_user(self, obj):
        if obj.user:
            url = reverse('admin:users_users_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user)
        return "-"

    view_user.short_description = "User"

    def view_addresses(self, obj):
        shipping = f"<strong>Shipping:</strong> {obj.shippingAddress}<br>" if obj.shippingAddress else ""
        billing = f"<strong>Billing:</strong> {obj.billingAddress}" if obj.billingAddress else ""
        return mark_safe(shipping + billing)

    view_addresses.short_description = "Addresses"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'shippingAddress', 'billingAddress'
        ).prefetch_related('items')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order_number', 'productName', 'quantity',
        'unitPrice', 'totalPrice', 'createdAt'
    ]
    list_filter = ['createdAt']
    search_fields = ['order__orderNumber', 'productName', 'productSku']
    readonly_fields = ['totalPrice', 'productName', 'productSku', 'createdAt']

    def order_number(self, obj):
        url = reverse('admin:carts_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.orderNumber)

    order_number.short_description = "Order"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transactionId', 'order_number', 'user', 'status',
        'amount', 'currency', 'razorpay_payment_id', 'createdAt'
    ]
    list_filter = ['status', 'currency', 'createdAt', 'completedAt']
    search_fields = [
        'transactionId', 'order__orderNumber', 'user__email',
        'razorpay_order_id', 'razorpay_payment_id'
    ]
    readonly_fields = [
        'transactionId', 'createdAt', 'updatedAt', 'completedAt',
        'view_gateway_response'
    ]

    fieldsets = (
        ('Transaction Information', {
            'fields': ('transactionId', 'user', 'order', 'status')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Gateway Response', {
            'fields': ('view_gateway_response', 'failureReason')
        }),
        ('Timestamps', {
            'fields': ('createdAt', 'updatedAt', 'completedAt')
        })
    )

    def order_number(self, obj):
        if obj.order:
            url = reverse('admin:carts_order_change', args=[obj.order.pk])
            return format_html('<a href="{}">{}</a>', url, obj.order.orderNumber)
        return "-"

    order_number.short_description = "Order"

    def view_gateway_response(self, obj):
        if obj.gatewayResponse:
            import json
            formatted_json = json.dumps(obj.gatewayResponse, indent=2)
            return format_html('<pre>{}</pre>', formatted_json)
        return "-"

    view_gateway_response.short_description = "Gateway Response"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'order')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'order_number', 'status', 'created_by_name',
        'notes_preview', 'createdAt'
    ]
    list_filter = ['status', 'createdAt']
    search_fields = ['order__orderNumber', 'notes', 'createdBy__email']
    readonly_fields = ['createdAt']

    def order_number(self, obj):
        url = reverse('admin:carts_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.orderNumber)

    order_number.short_description = "Order"

    def created_by_name(self, obj):
        return obj.createdBy if obj.createdBy else "System"

    created_by_name.short_description = "Created By"

    def notes_preview(self, obj):
        if obj.notes:
            return obj.notes[:50] + "..." if len(obj.notes) > 50 else obj.notes
        return "-"

    notes_preview.short_description = "Notes"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'createdBy')


# ============ CUSTOM ADMIN ACTIONS ============

@admin.action(description='Mark selected orders as shipped')
def mark_as_shipped(modeladmin, request, queryset):
    """Custom admin action to mark orders as shipped"""
    updated = 0
    for order in queryset:
        if order.status in ['CONFIRMED', 'PROCESSING', 'PACKED']:
            order.status = 'SHIPPED'
            order.save()

            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status='SHIPPED',
                notes='Marked as shipped via admin action',
                createdBy=request.user
            )
            updated += 1

    modeladmin.message_user(
        request,
        f'{updated} order(s) marked as shipped successfully.'
    )


@admin.action(description='Mark selected orders as delivered')
def mark_as_delivered(modeladmin, request, queryset):
    """Custom admin action to mark orders as delivered"""
    from django.utils import timezone

    updated = 0
    for order in queryset:
        if order.status in ['SHIPPED', 'OUT_FOR_DELIVERY']:
            order.status = 'DELIVERED'
            order.paymentStatus = 'PAID'
            order.deliveredAt = timezone.now()
            order.save()

            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status='DELIVERED',
                notes='Marked as delivered via admin action',
                createdBy=request.user
            )
            updated += 1

    modeladmin.message_user(
        request,
        f'{updated} order(s) marked as delivered successfully.'
    )


# Add custom actions to OrderAdmin
OrderAdmin.actions = [mark_as_shipped, mark_as_delivered]

# ============ ADMIN SITE CUSTOMIZATION ============

admin.site.site_header = "E-commerce Admin Panel"
admin.site.site_title = "E-commerce Admin"
admin.site.index_title = "Welcome to E-commerce Administration"