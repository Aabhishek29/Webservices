from django.urls import path
from .views import (category_list_create, subCategory_list_create,getSubCategorieById,
                    getProducts, getProductById, getProductBySubCategory,getProductBySKU)
from .dashboard import dashboardHome

urlpatterns = [
    path('', category_list_create, name='category-list-create'),
    path('subcategory/<uuid:categoryId>', getSubCategorieById, name='subcategory-list-create'),
    path('subcategory/', subCategory_list_create, name='subcategory-list-create'),
    path('products/', getProducts, name='get-products'),
    path('products/<sku>', getProductBySKU, name='product-detail'),
    path('products/productId/<uuid:productId>', getProductById, name='product-detail'),
    path('products/subcategory/<uuid:subCategoryId>', getProductBySubCategory, name='product-by-subcategories'),
    path('dashboard', dashboardHome, name='dashboard')
]