from rest_framework.permissions import AllowAny
from categories.models import (
    Products, ProductTag, ProductImage, ProductFeature,
    ProductMaterial, ProductStockModel, SubCategoriesModel, CategoriesModel
)
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from django.http import JsonResponse
from django.db.models import Prefetch


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def dashboardHome(request):
    """
    Dashboard API: Returns top 3 products from different subcategories across all categories.
    Products are ordered by totalSales (highest first) within each subcategory.
    """
    try:
        # Get all categories with their subcategories and products in one optimized query
        categories = CategoriesModel.objects.prefetch_related(
            'subcategories',
            'subcategories__products'
        ).all()
        print("Fetched categories:", categories)
        if not categories.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'No categories found',
                'data': []
            }, status=404)

        # Build response data
        response_data = []
        print("Building response data...")
        for category in categories:
            print(f"Processing category: {category.name}")
            category_data = {
                'categoryId': str(category.categoryId),
                'categoryName': category.name,
                'categoryImage': category.image.url if category.image else None,
                'subcategories': []
            }

            # Get subcategories for this category
            subcategories = category.subcategories.all()
            print(f"Found {len(subcategories)} subcategories for category {category.name}")
            for subcategory in subcategories:
                # Get top 3 products by totalSales for this subcategory
                top_products = Products.objects.filter(
                    subCategories=subcategory,
                    isActive=True
                ).select_related('subCategories').prefetch_related(
                    'images',
                    'tags',
                    'materials',
                    'keyFeatures',
                    'stocks'
                ).order_by('-totalSales', '-createdAt')[:3]

                if not top_products.exists():
                    continue
                print(f"Top products for subcategory {subcategory.name}: {[p.productName for p in top_products]}")
                # Serialize products for this subcategory
                products_list = []
                for product in top_products:
                    product_data = {
                        'productId': str(product.productId),
                        'productName': product.productName,
                        'description': product.description,
                        'price': str(product.price),
                        'SKU': product.SKU,
                        'discount': str(product.discount),
                        'discountPerc': str(product.discountPerc),
                        'discountedPrice': str(product.discounted_price),
                        'totalSales': product.totalSales,
                        'totalStock': product.total_stock,
                        'isActive': product.isActive,
                        'createdAt': product.createdAt.isoformat() if product.createdAt else None,
                        'updatedAt': product.updatedAt.isoformat() if product.updatedAt else None,
                        'images': [
                            {
                                'id': img.pk,  # Use pk instead of id
                                'image': img.image.url if img.image else None
                            }
                            for img in product.images.all()
                        ],
                        'tags': [tag.tag for tag in product.tags.all()],
                        'materials': [material.material for material in product.materials.all()],
                        'keyFeatures': [feature.feature for feature in product.keyFeatures.all()],
                        'stocks': [
                            {
                                'size': stock.size,
                                'quantity': stock.quantity,
                                'color': stock.color
                            }
                            for stock in product.stocks.all()
                        ]
                    }
                    products_list.append(product_data)
                print(f"Serialized products for subcategory {subcategory.name}: {products_list}")
                # Add subcategory with its products
                subcategory_data = {
                    'subCategoryId': str(subcategory.subCategoryId),
                    'subCategoryName': subcategory.name,
                    'collectionName': subcategory.collectionName,
                    'products': products_list
                }
                print(f"Adding subcategory data for {subcategory.name}: {subcategory_data}")
                category_data['subcategories'].append(subcategory_data)

            # Only include categories that have subcategories with products
            if category_data['subcategories']:
                response_data.append(category_data)

        # Calculate totals
        total_categories = len(response_data)
        total_subcategories = sum(len(cat['subcategories']) for cat in response_data)
        total_products = sum(
            len(subcat['products'])
            for cat in response_data
            for subcat in cat['subcategories']
        )
        print(f"Totals - Categories: {total_categories}, Subcategories: {total_subcategories}, Products: {total_products}")
        return JsonResponse({
            'status': 'success',
            'message': 'Successfully retrieved top 3 products from different subcategories',
            'totalCategories': total_categories,
            'totalSubcategories': total_subcategories,
            'totalProducts': total_products,
            'data': response_data
        }, status=200)

    except Exception as e:
        # Log the full error for debugging
        print(f"Dashboard API Error: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        print(f"Dashboard API Error: {error_trace}")

        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}',
            'data': []
        }, status=500)