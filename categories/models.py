from django.db import models
import uuid
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
        upload_to='categories/',  # Optional: folder path in your storage
        blank=True,
        null=True
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class SubCategoriesModel(models.Model):
    pass