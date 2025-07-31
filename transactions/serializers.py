from categories.models import Products
from users.models import Users
from .models import Wishlist, Cart
from rest_framework import serializers

class WishListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=Products.objects.all())
    class Meta:
        model = Wishlist
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = '__all__'