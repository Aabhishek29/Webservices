from rest_framework.permissions import AllowAny

from categories.models import Products, ProductTag, ProductImage, ProductFeature, ProductMaterial, ProductStockModel
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
import random
from django.http import JsonResponse
from collections import defaultdict


@api_view(['POST', 'GET'])
# @permission_classes([IsAuthenticated])
@authentication_classes([])
@permission_classes([AllowAny])
def dashboardHome(request):
    if request.method == "GET":
        try:
            # Get latest 50 products ordered by creation date (most recent first)
            products = Products.objects.filter(isActive=True).order_by('-createdAt')[:50]

            if not products:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No products found',
                    'data': []
                }, status=404)

            # Group products by tags
            products_by_tag = defaultdict(list)

            for product in products:
                # Get all tags for this product
                product_tags = ProductTag.objects.filter(product=product)

                if product_tags.exists():
                    # Add product to each tag group
                    for tag_obj in product_tags:
                        products_by_tag[tag_obj.tag].append(product)
                else:
                    # If product has no tags, add to 'untagged' group
                    products_by_tag['untagged'].append(product)

            # Randomly select 10 products ensuring variety across tags
            selected_products = []
            available_products = list(products)

            # If we have tagged products, try to get variety
            if products_by_tag:
                tag_keys = list(products_by_tag.keys())
                random.shuffle(tag_keys)

                # Try to pick products from different tags
                for tag in tag_keys:
                    if len(selected_products) >= 10:
                        break

                    tag_products = products_by_tag[tag]
                    # Remove already selected products from this tag
                    tag_products = [p for p in tag_products if p not in selected_products]

                    if tag_products:
                        selected_product = random.choice(tag_products)
                        selected_products.append(selected_product)

            # If we still need more products, randomly select from remaining
            remaining_products = [p for p in available_products if p not in selected_products]
            while len(selected_products) < 10 and remaining_products:
                selected_product = random.choice(remaining_products)
                selected_products.append(selected_product)
                remaining_products.remove(selected_product)

            # Serialize the selected products with related data
            products_data = []
            for product in selected_products:
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
                    'subCategories': product.subCategories.id if product.subCategories else None,
                    'discount': str(product.discount),
                    'discountPerc': str(product.discountPerc),
                    'totalSales': product.totalSales,
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
                products_data.append(product_dict)

            return JsonResponse({
                'status': 'success',
                'message': f'Successfully retrieved {len(products_data)} random products',
                'total_available': len(products),
                'data': products_data
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
            'message': 'Only POST method is allowed',
            'data': []
        }, status=405)