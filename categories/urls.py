from django.urls import path
from .views import category_list_create

urlpatterns = [
    path('', category_list_create, name='category-list-create'),
]
