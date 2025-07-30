from rest_framework import serializers
from .models import CategoriesModel, SubCategoriesModel
from .models import Products, ProductImage, ProductTag, ProductMaterial, ProductFeature, ProductStockModel


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = CategoriesModel
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    categories = serializers.PrimaryKeyRelatedField(queryset=CategoriesModel.objects.all())
    name = serializers.CharField(max_length=50)
    collectionName = serializers.CharField(max_length=30)

    class Meta:
        model = SubCategoriesModel
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = ['id', 'tag']


class ProductMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMaterial
        fields = ['id', 'material']


class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ['id', 'feature']


class ProductStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStockModel
        fields = ['id', 'size', 'quantity', 'color']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    tags = ProductTagSerializer(many=True, required=False)
    materials = ProductMaterialSerializer(many=True, required=False)
    keyFeatures = ProductFeatureSerializer(many=True, required=False)
    stocks = ProductStockSerializer(many=True, required=False)

    class Meta:
        model = Products
        fields = '__all__'

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        tags_data = validated_data.pop('tags', [])
        materials_data = validated_data.pop('materials', [])
        features_data = validated_data.pop('keyFeatures', [])
        stocks_data = validated_data.pop('stocks', [])

        product = Products.objects.create(**validated_data)

        for image in images_data:
            ProductImage.objects.create(product=product, **image)
        for tag in tags_data:
            ProductTag.objects.create(product=product, **tag)
        for material in materials_data:
            ProductMaterial.objects.create(product=product, **material)
        for feature in features_data:
            ProductFeature.objects.create(product=product, **feature)
        for stock in stocks_data:
            ProductStockModel.objects.create(product=product, **stock)

        return product