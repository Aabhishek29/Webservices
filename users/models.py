from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
import uuid


class Users(models.Model):
    userId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    firstName = models.CharField(max_length=25, default="", blank=True)
    lastName = models.CharField(max_length=25, default="", blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True)  # Will store hashed password
    phoneNumber = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)  # For OTP expiry
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phoneNumber'
    REQUIRED_FIELDS = []

    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password against stored hash"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f'{self.firstName} {self.lastName} - {self.phoneNumber}'


class Addresses(models.Model):
    addressId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='addresses')
    locationName = models.CharField(max_length=50, default="")
    streetAddress = models.CharField(max_length=100, default="")
    city = models.CharField(max_length=50, default="")
    state = models.CharField(max_length=50, default="")
    postalCode = models.CharField(max_length=6, default="")
    country = models.CharField(max_length=25, default="India")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.locationName} - {self.user.phoneNumber}"


class SubscriberModel(models.Model):
    subscriberId = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    email = models.EmailField(unique=True, null=False)
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='subscribers',
        null=True,  # Allow null in DB
        blank=True  # Allow blank in forms
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subscriberId} - {self.user.email if self.user else 'No User'}"

