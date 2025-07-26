from django.contrib import admin
from .models import Users, Addresses, SubscriberModel
# Register your models here.

admin.site.register(Users)
admin.site.register(Addresses)

admin.site.register(SubscriberModel)