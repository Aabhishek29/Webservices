from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .models import Wishlist, Cart, CartItem, Order, OrderItem, Transaction, OrderStatusHistory
from categories.models import Products
from users.models import Users, Addresses
from .serializers import (
    WishlistSerializer, CartSerializer, CartItemSerializer,
    AddToCartSerializer, UpdateCartItemSerializer, OrderSerializer,
    CreateOrderSerializer, OrderStatusUpdateSerializer, TransactionSerializer,
    PaymentInitiateSerializer, PaymentVerificationSerializer,
    OrderStatusHistorySerializer, OrderFilterSerializer
)


# ============ CUSTOM PAGINATION ============

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============ UTILITY FUNCTIONS ============

def get_user_by_id(user_id):
    """Get user by ID or raise 404"""
    return get_object_or_404(Users, pk=user_id)


# ============ WISHLIST VIEWS ============

@extend_schema(
    summary="Get user's wishlist",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH, required=True)
    ],
    responses=WishlistSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wishlist(request, user_id):
    """Get user's wishlist items"""
    user = get_user_by_id(user_id)

    # Optional: Check if requesting user has permission to view this wishlist
    if request.user != user and not request.user.is_staff:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    wishlist = Wishlist.objects.filter(user=user).select_related('product').order_by('-createdAt')
    serializer = WishlistSerializer(wishlist, many=True)

    return Response({
        'success': True,
        'data': serializer.data,
        'count': len(serializer.data)
    })


@extend_schema(
    summary="Add product to wishlist",
    request=WishlistSerializer,
    responses=WishlistSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
    """Add product to user's wishlist"""
    serializer = WishlistSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        try:
            wishlist_item = serializer.save()
            return Response({
                'success': True,
                'message': 'Product added to wishlist successfully',
                'data': WishlistSerializer(wishlist_item).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Remove product from wishlist",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH),
        OpenApiParameter('product_id', OpenApiTypes.UUID, OpenApiParameter.PATH)
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_wishlist(request, user_id, product_id):
    """Remove product from user's wishlist"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        wishlist_item = Wishlist.objects.get(user=user, product=product_id)
        wishlist_item.delete()

        return Response({
            'success': True,
            'message': 'Product removed from wishlist successfully'
        })
    except Wishlist.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Item not found in wishlist'
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="Clear user's wishlist",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH)
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_wishlist(request, user_id):
    """Clear all items from user's wishlist"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    deleted_count = Wishlist.objects.filter(user=user).delete()[0]

    return Response({
        'success': True,
        'message': f'Wishlist cleared successfully. {deleted_count} items removed.'
    })


# ============ CART VIEWS ============

@extend_schema(
    summary="Get user's cart",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH)
    ],
    responses=CartSerializer
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request, user_id):
    """Get or create user's cart"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response(
            {"error": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    cart, created = Cart.objects.get_or_create(user=user)
    serializer = CartSerializer(cart)

    return Response({
        'success': True,
        'data': serializer.data,
        'is_new_cart': created
    })


@extend_schema(
    summary="Add item to cart",
    request=AddToCartSerializer,
    responses=CartSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Add item to user's cart"""
    serializer = AddToCartSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data['user_id']
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        size = serializer.validated_data['size']
        color = serializer.validated_data['color']

        user = get_user_by_id(user_id)

        # Check permission
        if request.user != user and not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                product = get_object_or_404(Products, pk=product_id)
                cart, created = Cart.objects.get_or_create(user=user)

                # Check if item with same size and color already exists in cart
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    size=size,
                    color=color,
                    defaults={'quantity': quantity}
                )

                if not item_created:
                    cart_item.quantity += quantity
                    cart_item.save()
                    message = f'Updated quantity to {cart_item.quantity} for size {size}, color {color}'
                else:
                    message = f'Item added to cart successfully (Size: {size}, Color: {color})'

                # Return updated cart
                cart_serializer = CartSerializer(cart)
                return Response({
                    'success': True,
                    'message': message,
                    'data': cart_serializer.data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Update cart item quantity",
    request=UpdateCartItemSerializer,
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH),
        OpenApiParameter('item_id', OpenApiTypes.INT, OpenApiParameter.PATH)
    ],
    responses=CartSerializer
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, user_id, item_id):
    """Update cart item quantity"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        cart_item = CartItem.objects.get(
            id=item_id,
            cart__user=user
        )
    except CartItem.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cart item not found'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateCartItemSerializer(data=request.data, instance=cart_item)

    if serializer.is_valid():
        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()

        cart_serializer = CartSerializer(cart_item.cart)
        return Response({
            'success': True,
            'message': 'Cart item updated successfully',
            'data': cart_serializer.data
        })

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Remove item from cart",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH),
        OpenApiParameter('item_id', OpenApiTypes.INT, OpenApiParameter.PATH)
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, user_id, item_id):
    """Remove item from user's cart"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        cart_item = CartItem.objects.get(
            id=item_id,
            cart__user=user
        )
        product_name = cart_item.product.productName
        cart_item.delete()

        return Response({
            'success': True,
            'message': f'{product_name} removed from cart successfully'
        })
    except CartItem.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cart item not found'
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="Clear user's cart",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH)
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request, user_id):
    """Clear all items from user's cart"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        cart = Cart.objects.get(user=user)
        items_count = cart.items.count()
        cart.items.all().delete()

        return Response({
            'success': True,
            'message': f'Cart cleared successfully. {items_count} items removed.'
        })
    except Cart.DoesNotExist:
        return Response({
            'success': True,
            'message': 'Cart is already empty'
        })


# ============ ORDER VIEWS ============

@extend_schema(
    summary="Get user's order history",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH),
        OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter('payment_status', OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY),
        OpenApiParameter('page_size', OpenApiTypes.INT, OpenApiParameter.QUERY)
    ],
    responses=OrderSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_history(request, user_id):
    """Get user's order history with filtering"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)

    # Apply filters
    orders = Order.objects.filter(user=user).prefetch_related('items__product')

    # Status filter
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Payment status filter
    payment_status = request.GET.get('payment_status')
    if payment_status:
        orders = orders.filter(paymentStatus=payment_status)

    # Search filter (order number or product name)
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(orderNumber__icontains=search) |
            Q(items__productName__icontains=search)
        ).distinct()

    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        orders = orders.filter(createdAt__date__gte=date_from)
    if date_to:
        orders = orders.filter(createdAt__date__lte=date_to)

    # Pagination
    paginator = StandardResultsSetPagination()
    paginated_orders = paginator.paginate_queryset(orders, request)

    serializer = OrderSerializer(paginated_orders, many=True)

    return paginator.get_paginated_response({
        'success': True,
        'data': serializer.data
    })


@extend_schema(
    summary="Get specific order details",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH),
        OpenApiParameter('order_id', OpenApiTypes.UUID, OpenApiParameter.PATH)
    ],
    responses=OrderSerializer
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_details(request, user_id, order_id):
    """Get specific order details"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        order = Order.objects.select_related(
            'shippingAddress', 'billingAddress'
        ).prefetch_related(
            'items__product', 'status_history'
        ).get(orderId=order_id, user=user)

        serializer = OrderSerializer(order)

        # Get status history
        status_history = OrderStatusHistorySerializer(
            order.status_history.all()[:10],
            many=True
        ).data

        response_data = serializer.data
        response_data['status_history'] = status_history

        return Response({
            'success': True,
            'data': response_data
        })

    except Order.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="Create new order from cart",
    request=CreateOrderSerializer,
    responses=OrderSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create new order from user's cart"""
    serializer = CreateOrderSerializer(data=request.data)

    if serializer.is_valid():
        user_id = serializer.validated_data['user_id']
        user = get_user_by_id(user_id)

        # Check permission
        if request.user != user and not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                # Get user's cart
                cart = Cart.objects.get(user=user)
                cart_items = cart.items.all()

                if not cart_items.exists():
                    return Response({
                        'success': False,
                        'error': 'Cart is empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Create order
                order_data = {
                    'user': user,
                    'shippingAddress': get_object_or_404(
                        Addresses, pk=serializer.validated_data['shipping_address_id']
                    ),
                    'notes': serializer.validated_data.get('notes', ''),
                    'isGift': serializer.validated_data.get('is_gift', False),
                    'giftMessage': serializer.validated_data.get('gift_message', '')
                }

                if serializer.validated_data.get('billing_address_id'):
                    order_data['billingAddress'] = get_object_or_404(
                        Addresses, pk=serializer.validated_data['billing_address_id']
                    )

                order = Order.objects.create(**order_data)

                # Create order items
                total_amount = 0
                for cart_item in cart_items:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        size=cart_item.size,
                        color=cart_item.color,
                        unitPrice=cart_item.product.price
                    )
                    total_amount += order_item.totalPrice

                # Update order totals
                order.subtotal = total_amount
                order.totalAmount = total_amount  # Add tax/shipping calculation here
                order.save()

                # Create status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status='PENDING',
                    notes='Order created',
                    createdBy=request.user
                )

                # Clear cart
                cart_items.delete()

                order_serializer = OrderSerializer(order)
                return Response({
                    'success': True,
                    'message': 'Order created successfully',
                    'data': order_serializer.data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Update order status",
    request=OrderStatusUpdateSerializer,
    parameters=[
        OpenApiParameter('order_id', OpenApiTypes.UUID, OpenApiParameter.PATH)
    ]
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status (Admin only)"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied. Admin access required.'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        order = Order.objects.get(orderId=order_id)
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderStatusUpdateSerializer(data=request.data)

    if serializer.is_valid():
        old_status = order.status
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')
        tracking_id = serializer.validated_data.get('tracking_id', '')

        # Update order
        order.status = new_status
        if tracking_id:
            order.trackingId = tracking_id

        if new_status == 'DELIVERED':
            order.deliveredAt = timezone.now()
            order.paymentStatus = 'PAID'  # Assume payment is confirmed on delivery

        order.save()

        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=notes or f'Status changed from {old_status} to {new_status}',
            createdBy=request.user
        )

        order_serializer = OrderSerializer(order)
        return Response({
            'success': True,
            'message': f'Order status updated to {new_status}',
            'data': order_serializer.data
        })

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Cancel order",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH),
        OpenApiParameter('order_id', OpenApiTypes.UUID, OpenApiParameter.PATH)
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, user_id, order_id):
    """Cancel an order"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        order = Order.objects.get(orderId=order_id, user=user)

        # Check if order can be cancelled
        if order.status in ['DELIVERED', 'CANCELLED', 'RETURNED']:
            return Response({
                'success': False,
                'error': f'Cannot cancel order with status: {order.status}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cancel order
        order.status = 'CANCELLED'
        order.save()

        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='CANCELLED',
            notes='Order cancelled by user',
            createdBy=request.user
        )

        return Response({
            'success': True,
            'message': 'Order cancelled successfully'
        })

    except Order.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)


# ============ TRANSACTION VIEWS ============

@extend_schema(
    summary="Get user's transaction history",
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, OpenApiParameter.PATH)
    ],
    responses=TransactionSerializer(many=True)
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request, user_id):
    """Get user's transaction history"""
    user = get_user_by_id(user_id)

    # Check permission
    if request.user != user and not request.user.is_staff:
        return Response({
            'success': False,
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)

    transactions = Transaction.objects.filter(user=user).select_related('order')

    # Pagination
    paginator = StandardResultsSetPagination()
    paginated_transactions = paginator.paginate_queryset(transactions, request)

    serializer = TransactionSerializer(paginated_transactions, many=True)

    return paginator.get_paginated_response({
        'success': True,
        'data': serializer.data
    })