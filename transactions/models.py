import uuid
from users.models import Users, Addresses
from categories.models import Products
from django.db import models

# Create your models here.

class Cart(models.Model):
    cartId = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='cartProduct')
    quantity = models.PositiveIntegerField(default=1)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart {self.cartId}'

ORDER_STATUS = (
    ('PENDING', 'Pending'),
    ('PAID', 'Paid'),
    ('FAILED', 'Failed'),
    ('SHIPPED', 'Shipped'),
    ('DELIVERED', 'Delivered'),
)

class Order(models.Model):
    orderId = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='orders')
    shippingAddress = models.ForeignKey(Addresses, on_delete=models.CASCADE, related_name='orders')
    trackingId = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.orderId)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class TransactionModel(models.Model):
    transactionId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transaction')

    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100)
    razorpay_signature = models.CharField(max_length=255)

    amountPaid = models.DecimalField(max_digits=10, decimal_places=2)
    createdAt = models.DateTimeField(auto_now_add=True)


class Wishlist(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate wishlist entries

    def __str__(self):
        return f'{self.user.firstName} - {self.product.productName}'



