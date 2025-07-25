from django.db import models
import uuid
# Create your models here.

class Users(models.Model):
    userId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    firstName = models.CharField(max_length=25, default="UnKnown", blank=True)
    lastName = models.CharField(max_length=25, default="", blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phoneNumber = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6, blank=True)
    is_verified = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.firstName}  {self.phoneNumber}'


class Addresses(models.Model):
    addressId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='addresses')
    locationName = models.CharField(max_length=50, default="")
    streetAddress = models.CharField(max_length=100, default="")
    city = models.CharField(max_length=50, default="")
    state = models.CharField(max_length=50, default="")
    postalCode = models.CharField(max_length=6, default="")
    country = models.CharField(max_length=25, default="")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.locationName} - {self.user.phoneNumber}"