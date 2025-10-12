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

    @property
    def id(self):
        """Alias for subCategoryId to support legacy code"""
        return self.subCategoryId

    def __str__(self):
        return self.name


class Products(models.Model):
    productId = models.UUIDField(primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    productName = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    SKU = models.CharField(max_length=50, unique=True, blank=True)
    subCategories = models.ForeignKey('SubCategoriesModel', on_delete=models.CASCADE, related_name='products')
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    discountPerc = models.DecimalField(max_digits=5, decimal_places=2)
    totalSales = models.IntegerField(default=0)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.productName

    @property
    def total_stock(self):
        """Get total stock across all sizes and colors"""
        return self.stocks.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def discounted_price(self):
        """Calculate discounted price"""
        if self.discount > 0:
            return self.price - self.discount
        elif self.discountPerc > 0:
            return self.price * (1 - self.discountPerc / 100)
        return self.price

    def has_stock(self, quantity=1, size=None, color=None):
        """Check if product has enough stock for specific size/color or total"""
        if size is not None and color is not None:
            # Check stock for specific variant
            try:
                stock_item = self.stocks.get(size=size, color=color)
                return stock_item.quantity >= quantity
            except:
                return False
        else:
            # Check total stock across all variants
            return self.total_stock >= quantity

    def get_variant_stock(self, size, color):
        """Get stock quantity for specific size/color variant"""
        try:
            stock_item = self.stocks.get(size=size, color=color)
            return stock_item.quantity
        except:
            return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')

    def __str__(self):
        return f"Image for {self.product.productName}"


class ProductTag(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tag} (Product: {self.product.productName})"


class ProductMaterial(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='materials')
    material = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.material} (Product: {self.product.productName})"


class ProductFeature(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='keyFeatures')
    feature = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.feature} (Product: {self.product.productName})"


class ProductStockModel(models.Model):
    size = models.IntegerField(blank=False)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.IntegerField(blank=False, default=0)
    color = models.CharField(max_length=9)

    def __str__(self):
        return f"(Product: {self.product.productName})"




