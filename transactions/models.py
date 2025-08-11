import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import Users, Addresses
from categories.models import Products


# Create your models here.

class Cart(models.Model):
    cartId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='cart')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart - {self.user.username if hasattr(self.user, 'username') else self.user}"

    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def items_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(999)]
    )
    addedAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['-updatedAt']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.product.price

    @property
    def unit_price(self):
        return self.product.price


class Wishlist(models.Model):
    wishlistId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='wishlist_items')
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        db_table = 'wishlists'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'
        ordering = ['-createdAt']

    def __str__(self):
        return f'{self.user} - {self.product.name}'


ORDER_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('PROCESSING', 'Processing'),
    ('PACKED', 'Packed'),
    ('SHIPPED', 'Shipped'),
    ('OUT_FOR_DELIVERY', 'Out for Delivery'),
    ('DELIVERED', 'Delivered'),
    ('CANCELLED', 'Cancelled'),
    ('RETURNED', 'Returned'),
    ('REFUNDED', 'Refunded'),
)

PAYMENT_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('PAID', 'Paid'),
    ('FAILED', 'Failed'),
    ('REFUNDED', 'Refunded'),
    ('PARTIALLY_REFUNDED', 'Partially Refunded'),
)


class Order(models.Model):
    orderId = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    orderNumber = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='orders')
    shippingAddress = models.ForeignKey(
        Addresses,
        on_delete=models.PROTECT,
        related_name='shipping_orders'
    )
    billingAddress = models.ForeignKey(
        Addresses,
        on_delete=models.PROTECT,
        related_name='billing_orders',
        null=True,
        blank=True
    )

    # Order Status and Tracking
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    paymentStatus = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    trackingId = models.CharField(max_length=100, blank=True, null=True)

    # Financial Information
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    taxAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shippingAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discountAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    totalAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Payment Gateway Information
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)

    # Timestamps
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    deliveredAt = models.DateTimeField(null=True, blank=True)

    # Additional Information
    notes = models.TextField(blank=True, null=True)
    isGift = models.BooleanField(default=False)
    giftMessage = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-createdAt']

    def save(self, *args, **kwargs):
        if not self.orderNumber:
            # Generate order number like ORD-2024-000001
            from django.utils import timezone
            year = timezone.now().year
            last_order = Order.objects.filter(
                orderNumber__startswith=f'ORD-{year}-'
            ).order_by('-orderNumber').first()

            if last_order:
                last_number = int(last_order.orderNumber.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.orderNumber = f'ORD-{year}-{new_number:06d}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.orderNumber} - {self.user}"

    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def calculate_totals(self):
        """Calculate and update order totals"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        # Add tax calculation logic here if needed
        self.totalAmount = self.subtotal + self.taxAmount + self.shippingAmount - self.discountAmount
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2)
    totalPrice = models.DecimalField(max_digits=12, decimal_places=2)

    # Product snapshot for historical data
    productName = models.CharField(max_length=255)
    productSku = models.CharField(max_length=100, blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.productName = self.product.name
            self.unitPrice = self.product.price
            if hasattr(self.product, 'sku'):
                self.productSku = self.product.sku

        self.totalPrice = self.quantity * self.unitPrice
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.productName} x {self.quantity}"


TRANSACTION_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('SUCCESS', 'Success'),
    ('FAILED', 'Failed'),
    ('REFUNDED', 'Refunded'),
    ('CANCELLED', 'Cancelled'),
)


class Transaction(models.Model):
    transactionId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='transactions')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')

    # Payment Gateway Information
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)

    # Transaction Details
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')

    # Gateway Response
    gatewayResponse = models.JSONField(blank=True, null=True)
    failureReason = models.TextField(blank=True, null=True)

    # Timestamps
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    completedAt = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-createdAt']

    def __str__(self):
        return f"Transaction {self.transactionId} - {self.status}"


class OrderStatusHistory(models.Model):
    """Track order status changes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    createdBy = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_updates'
    )
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_status_history'
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['-createdAt']

    def __str__(self):
        return f"Order {self.order.orderNumber} - {self.status}"