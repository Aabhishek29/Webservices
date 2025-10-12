from rest_framework.permissions import AllowAny

from categories.models import (
    Products, ProductTag, ProductImage, ProductFeature,
    ProductMaterial, ProductStockModel, SubCategoriesModel, CategoriesModel
)
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
import random
from django.http import JsonResponse
from collections import defaultdict


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def dashboardHome(request):
    """
    Dashboard API: Returns top 3 products from different subcategories across all categories
    """
    if request.method == "GET":
        try:
            # Get all active categories
            categories = CategoriesModel.objects.all()

            if not categories.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'No categories found',
                    'data': []
                }, status=404)

            # Group products by subcategory
            products_by_subcategory = {}
            all_subcategories = SubCategoriesModel.objects.all()

            for subcategory in all_subcategories:
                # Get top 3 products by totalSales for each subcategory
                top_products = Products.objects.filter(
                    subCategories=subcategory,
                    isActive=True
                ).order_by('-totalSales', '-createdAt')[:3]

                if top_products.exists():
                    products_by_subcategory[subcategory] = list(top_products)

            # Prepare response data grouped by categories
            categories_data = []

            for category in categories:
                # Get subcategories for this category
                subcategories = category.subcategories.all()

                category_products = []
                for subcategory in subcategories:
                    if subcategory in products_by_subcategory:
                        # Serialize products for this subcategory
                        for product in products_by_subcategory[subcategory]:
                            # Get related data
                            images = ProductImage.objects.filter(product=product)
                            tags = ProductTag.objects.filter(product=product)
                            materials = ProductMaterial.objects.filter(product=product)
                            features = ProductFeature.objects.filter(product=product)
                            stocks = ProductStockModel.objects.filter(product=product)

                            product_dict = {
                                'productId': str(product.productId),
                                'productName': product.productName,
                                'description': product.description,
                                'price': str(product.price),
                                'SKU': product.SKU,
                                'subCategoryId': str(product.subCategories.subCategoryId),
                                'subCategoryName': product.subCategories.name,
                                'discount': str(product.discount),
                                'discountPerc': str(product.discountPerc),
                                'discountedPrice': str(product.discounted_price),
                                'totalSales': product.totalSales,
                                'totalStock': product.total_stock,
                                'isActive': product.isActive,
                                'createdAt': product.createdAt.isoformat(),
                                'updatedAt': product.updatedAt.isoformat(),
                                'images': [{'id': img.id, 'image': img.image.url if img.image else None} for img in images],
                                'tags': [tag.tag for tag in tags],
                                'materials': [material.material for material in materials],
                                'keyFeatures': [feature.feature for feature in features],
                                'stocks': [{
                                    'size': stock.size,
                                    'quantity': stock.quantity,
                                    'color': stock.color
                                } for stock in stocks]
                            }
                            category_products.append(product_dict)

                # Only add category if it has products
                if category_products:
                    categories_data.append({
                        'categoryId': str(category.categoryId),
                        'categoryName': category.name,
                        'categoryImage': category.image.url if category.image else None,
                        'products': category_products
                    })

            # Calculate total products
            total_products = sum(len(cat['products']) for cat in categories_data)

            return JsonResponse({
                'status': 'success',
                'message': f'Successfully retrieved top 3 products from different subcategories',
                'totalCategories': len(categories_data),
                'totalProducts': total_products,
                'data': categories_data
            }, status=200)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}',
                'data': []
            }, status=500)

    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only GET method is allowed',
            'data': []
        }, status=405)