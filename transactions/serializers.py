from rest_framework import serializers
from django.db import transaction
from categories.models import Products
from users.models import Users, Addresses
from .models import (
    Wishlist, Cart, CartItem, Order, OrderItem,
    Transaction, OrderStatusHistory
)


# ============ WISHLIST SERIALIZERS ============

class WishlistProductSerializer(serializers.ModelSerializer):
    """Nested product serializer for wishlist"""

    class Meta:
        model = Products
        fields = ['productId', 'name', 'price', 'discountedPrice', 'image']


class WishlistSerializer(serializers.ModelSerializer):
    product = WishlistProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ['wishlistId', 'product', 'product_id', 'createdAt']
        read_only_fields = ['wishlistId', 'createdAt']

    def validate_product_id(self, value):
        try:
            Products.objects.get(pk=value)
            return value
        except Products.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")

    def create(self, validated_data):
        user = self.context['request'].user
        product_id = validated_data.pop('product_id')
        product = Products.objects.get(pk=product_id)

        # Check if already in wishlist
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Product already in wishlist")

        return Wishlist.objects.create(user=user, product=product)


# ============ CART SERIALIZERS ============

class CartItemProductSerializer(serializers.ModelSerializer):
    """Nested product serializer for cart items"""

    class Meta:
        model = Products
        fields = ['productId', 'name', 'price', 'discountedPrice', 'image', 'inStock']


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer(read_only=True)
    unit_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'quantity', 'unit_price',
            'total_price', 'addedAt', 'updatedAt'
        ]
        read_only_fields = ['id', 'addedAt', 'updatedAt']

    def get_total_price(self, obj):
        return obj.total_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'cartId', 'user', 'items', 'total_items',
            'total_amount', 'items_count', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['cartId', 'user', 'createdAt', 'updatedAt']

    def get_total_items(self, obj):
        return obj.total_items

    def get_total_amount(self, obj):
        return obj.total_amount

    def get_items_count(self, obj):
        return obj.items_count


class AddToCartSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, max_value=999, default=1)

    def validate_user_id(self, value):
        try:
            Users.objects.get(pk=value)
            return value
        except Users.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

    def validate_product_id(self, value):
        try:
            product = Products.objects.get(pk=value)
            if not product.inStock:
                raise serializers.ValidationError("Product is out of stock.")
            return value
        except Products.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")

    def validate(self, attrs):
        product = Products.objects.get(pk=attrs['product_id'])
        if hasattr(product, 'stock') and product.stock < attrs['quantity']:
            raise serializers.ValidationError(
                f"Only {product.stock} items available in stock."
            )
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, max_value=999)

    def validate_quantity(self, value):
        if hasattr(self, 'instance') and self.instance:
            product = self.instance.product
            if hasattr(product, 'stock') and product.stock < value:
                raise serializers.ValidationError(
                    f"Only {product.stock} items available in stock."
                )
        return value


# ============ ORDER SERIALIZERS ============

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='productName', read_only=True)
    product_id = serializers.UUIDField(source='product.productId', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name', 'quantity',
            'unitPrice', 'totalPrice', 'productSku'
        ]
        read_only_fields = ['id', 'unitPrice', 'totalPrice', 'productSku']


class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addresses
        fields = ['addressId', 'street', 'city', 'state', 'zipCode', 'country']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shippingAddress = OrderAddressSerializer(read_only=True)
    billingAddress = OrderAddressSerializer(read_only=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'orderId', 'orderNumber', 'user', 'status', 'paymentStatus',
            'trackingId', 'subtotal', 'taxAmount', 'shippingAmount',
            'discountAmount', 'totalAmount', 'items', 'total_items',
            'shippingAddress', 'billingAddress', 'notes', 'isGift',
            'giftMessage', 'createdAt', 'updatedAt', 'deliveredAt'
        ]
        read_only_fields = [
            'orderId', 'orderNumber', 'createdAt', 'updatedAt'
        ]

    def get_total_items(self, obj):
        return obj.total_items


class CreateOrderSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    shipping_address_id = serializers.UUIDField()
    billing_address_id = serializers.UUIDField(required=False, allow_null=True)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    is_gift = serializers.BooleanField(default=False)
    gift_message = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_user_id(self, value):
        try:
            Users.objects.get(pk=value)
            return value
        except Users.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

    def validate_shipping_address_id(self, value):
        try:
            Addresses.objects.get(pk=value)
            return value
        except Addresses.DoesNotExist:
            raise serializers.ValidationError("Shipping address does not exist.")

    def validate_billing_address_id(self, value):
        if value:
            try:
                Addresses.objects.get(pk=value)
                return value
            except Addresses.DoesNotExist:
                raise serializers.ValidationError("Billing address does not exist.")
        return value

    def validate(self, attrs):
        user = Users.objects.get(pk=attrs['user_id'])

        # Check if user has items in cart
        try:
            cart = Cart.objects.get(user=user)
            if not cart.items.exists():
                raise serializers.ValidationError("Cart is empty.")
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart does not exist.")

        return attrs


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURNED', 'Returned'),
    ])
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    tracking_id = serializers.CharField(max_length=100, required=False, allow_blank=True)


# ============ TRANSACTION SERIALIZERS ============

class TransactionSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.orderNumber', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'transactionId', 'order', 'order_number', 'status',
            'amount', 'currency', 'razorpay_order_id',
            'razorpay_payment_id', 'failureReason',
            'createdAt', 'completedAt'
        ]
        read_only_fields = [
            'transactionId', 'createdAt', 'completedAt'
        ]


class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()

    def validate_order_id(self, value):
        try:
            order = Order.objects.get(pk=value)
            if order.paymentStatus == 'PAID':
                raise serializers.ValidationError("Order is already paid.")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order does not exist.")


class PaymentVerificationSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField(max_length=100)
    razorpay_payment_id = serializers.CharField(max_length=100)
    razorpay_signature = serializers.CharField(max_length=500)


# ============ ORDER HISTORY SERIALIZERS ============

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='createdBy.username', read_only=True, allow_null=True)

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'created_by_name', 'createdAt']
        read_only_fields = ['id', 'createdAt']


# ============ FILTER SERIALIZERS ============

class OrderFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[('', 'All')] + list(Order._meta.get_field('status').choices),
        required=False,
        allow_blank=True
    )
    payment_status = serializers.ChoiceField(
        choices=[('', 'All')] + list(Order._meta.get_field('paymentStatus').choices),
        required=False,
        allow_blank=True
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    search = serializers.CharField(max_length=100, required=False, allow_blank=True)