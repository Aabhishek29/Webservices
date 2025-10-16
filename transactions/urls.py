from django.urls import path
from . import views

urlpatterns = [
    # ============ WISHLIST URLs ============
    path('wishlist/<uuid:user_id>/', views.get_wishlist, name='get-wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/<uuid:user_id>/remove/<uuid:product_id>/', views.remove_from_wishlist, name='remove-from-wishlist'),
    path('wishlist/<uuid:user_id>/clear/', views.clear_wishlist, name='clear-wishlist'),

    # ============ CART URLs ============
    path('cart/<uuid:user_id>/', views.get_cart, name='get-cart'),
    path('cart/add', views.add_to_cart, name='add-to-cart'),
    path('cart/add/', views.add_to_cart, name='add-to-cart-slash'),
    path('cart/<uuid:user_id>/update/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/<uuid:user_id>/remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('cart/<uuid:user_id>/clear/', views.clear_cart, name='clear-cart'),

    # ============ ORDER URLs ============
    path('orders/<uuid:user_id>/', views.order_history, name='order-history'),
    path('orders/<uuid:user_id>/<uuid:order_id>/', views.get_order_details, name='order-details'),
    path('orders/create/', views.create_order, name='create-order'),
    path('orders/<uuid:order_id>/status/', views.update_order_status, name='update-order-status'),
    path('orders/<uuid:user_id>/<uuid:order_id>/cancel/', views.cancel_order, name='cancel-order'),

    # ============ TRANSACTION URLs ============
    path('transactions/<uuid:user_id>/', views.transaction_history, name='transaction-history'),

    # ============ PAYMENT URLs ============
    path('payment/create-razorpay-order/', views.create_razorpay_order, name='create-razorpay-order'),
    path('payment/verify-payment/', views.verify_razorpay_payment, name='verify-razorpay-payment'),
    path('payment/razorpay-key/', views.get_razorpay_key, name='get-razorpay-key'),
]