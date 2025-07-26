from django.db import models
import uuid
from django.contrib.postgres.fields import ArrayField
# Create your models here.


class CategoriesModel(models.Model):
    categoryId = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        blank=False
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=False,
        null=False
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class SubCategoriesModel(models.Model):
    subCategoryId = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    categories = models.ForeignKey(CategoriesModel, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(
        max_length=50,
        unique=True,
        blank=False
    )
    collectionName = models.CharField(max_length=30, blank=False)
    image = models.ImageField(
        upload_to='subCategories/',
        blank=False,
        null=False
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Products(models.Model):
    productName = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=False)
    keyFeatures = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    material = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    SKU = models.CharField(max_length=50, unique=True, blank=True)
    subCategories = models.ForeignKey(SubCategoriesModel, on_delete=models.CASCADE, related_name='products')
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    discountPerc = models.DecimalField(max_digits=2, decimal_places=2)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    images = ArrayField(models.ImageField(
        upload_to=f'products/{productName}',
        blank=False,
        null=False
    ))


    def __str__(self):
        return self.productName

