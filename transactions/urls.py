from django.urls import path
from .views import wish_list_by_user


urlpatterns = [
    path('wishlist/', wish_list_by_user, name='get-wishlist-by-user'),
]