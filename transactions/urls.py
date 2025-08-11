from django.urls import path
from .views import wish_list_by_user, orderHistoryByUserId


urlpatterns = [
    path('wishlist/', wish_list_by_user, name='get-wishlist-by-user'),
    path('order_history/<uuid:userId>', orderHistoryByUserId, name='get-order-history-by-userId')
]