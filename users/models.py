from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid

class UserManager(BaseUserManager):
    def create_user(self, phoneNumber, email=None, password=None, **extra_fields):
        if not phoneNumber:
            raise ValueError('The Phone Number field must be set')
        
        user = self.model(phoneNumber=phoneNumber, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phoneNumber, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phoneNumber, email, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    userId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    firstName = models.CharField(max_length=25, default="UnKnown", blank=True)
    lastName = models.CharField(max_length=25, default="", blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phoneNumber = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phoneNumber'
    REQUIRED_FIELDS = []

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

