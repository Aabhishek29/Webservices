from django.urls import path
from .views import getWishListByUserId


urlpatterns = [
    path('wishlist/', getWishListByUserId, name='get-wishlist-by-user'),
]