from django.urls import path
from .views import (category_list_create, subCategory_list_create,getSubCategorieById,
                    getProducts, getProductById, getProductBySubCategory)

urlpatterns = [
    path('', category_list_create, name='category-list-create'),
    path('subcategory/<uuid:categoryId>', getSubCategorieById, name='subcategory-list-create'),
    path('subcategory/', subCategory_list_create, name='subcategory-list-create'),
    path('products/', getProducts, name='get-products'),
    path('products/<sku>', getProductById, name='product-detail'),
    path('products/subcategory/<uuid:subCategoryId>', getProductBySubCategory, name='product-by-subcategories')
]