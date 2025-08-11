from drf_spectacular.utils import extend_schema
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from yaml import serialize

from .models import CategoriesModel, SubCategoriesModel, Products
from .serializers import CategorySerializer, SubCategorySerializer, ProductSerializer



@extend_schema(request=CategorySerializer)
@api_view(['POST', 'GET'])
# @permission_classes([IsAuthenticated])
@authentication_classes([])           # ← No authentication required
@permission_classes([AllowAny])
def category_list_create(request):
    # if request.method == 'POST':
    #     serializer = CategorySerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({
    #             'message': 'Category created successfully',
    #             'data': serializer.data
    #         }, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        categories = CategoriesModel.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "success": True,
            "categories": serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Method not allowed', 'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(request=SubCategorySerializer)
@api_view(['POST', 'GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def getSubCategorieById(request, categoryId):
    try:
        subCategory = SubCategoriesModel.objects.filter(categories=categoryId)
        if not subCategory.exists():
            return Response({'error': 'No subCategory found in this category'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubCategorySerializer(subCategory, many=True)
        return Response({
            "success": True,
            "subCategory": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e), 'success': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(request=SubCategorySerializer)
@api_view(['POST', 'GET'])
@authentication_classes([])           # ← No authentication required
@permission_classes([AllowAny])
def subCategory_list_create(request):
    # if request.method == 'POST':
    #     serializer = SubCategorySerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({
    #             'message': 'SubCategory created successfully',
    #             'data': serializer.data
    #         }, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        subCategories = SubCategoriesModel.objects.all()
        serializer = SubCategorySerializer(subCategories, many=True)
        return Response({
            'success': True,
            'subCategories': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Method not allowed', 'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(request=ProductSerializer)
@api_view(['POST', 'GET'])
@authentication_classes([])           # ← No authentication required
@permission_classes([AllowAny])
def getProducts(request):
    if request.method == 'GET':
        products = Products.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    else:
        return Response({'error': 'Method not allowed', 'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(request=ProductSerializer)
@api_view(['GET'])
@authentication_classes([])           # ← No authentication required
@permission_classes([AllowAny])
def getProducts(request):
    if request.method == 'GET':
        products = Products.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    return Response({'error': 'Method not allowed', 'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(request=ProductSerializer)
@api_view(['GET'])
@authentication_classes([])           # ← No authentication required
@permission_classes([AllowAny])
def getProductBySKU(request, sku):
    if request.method == 'GET':
        try:
            product = Products.objects.get(SKU=sku)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'Method not allowed', 'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(request=ProductSerializer)
@api_view(['GET'])
@authentication_classes([])           # ← No authentication required
@permission_classes([AllowAny])
def getProductById(request, productId):
    if request.method == 'GET':
        try:
            product = Products.objects.get(productId=productId)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'Method not allowed', 'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@authentication_classes([])           # ← No authentication required
@permission_classes([AllowAny])
def getProductBySubCategory(request, subCategoryId):
    try:
        products = Products.objects.filter(subCategories=subCategoryId)
        if not products.exists():
            return Response({'error': 'No products found in this subcategory'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e), 'success': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)