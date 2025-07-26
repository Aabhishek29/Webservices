from django.contrib import admin
from .models import CategoriesModel,SubCategoriesModel
from django.contrib import admin
from .models import Products, ProductImage, ProductTag, ProductMaterial, ProductFeature,ProductStockModel


admin.site.register(CategoriesModel)
admin.site.register(SubCategoriesModel)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductTagInline(admin.TabularInline):
    model = ProductTag
    extra = 1

class ProductMaterialInline(admin.TabularInline):
    model = ProductMaterial
    extra = 1

class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1

class ProductStockInline(admin.TabularInline):
    model = ProductStockModel
    extra = 1

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductTagInline, ProductMaterialInline, ProductFeatureInline, ProductStockInline]
    list_display = ('productName', 'SKU', 'price', 'discount', 'discountPerc')