from rest_framework import serializers
from .models import CategoriesModel

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = CategoriesModel
        fields = '__all__'
