from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import CategoriesModel
from .serializers import CategorySerializer
from django.core.files.storage import default_storage



@extend_schema(request=CategorySerializer)
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def category_list_create(request):
    if request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Category created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        categories = CategoriesModel.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)



