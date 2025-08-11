from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Wishlist, Cart
from drf_spectacular.utils import extend_schema
from .serializers import WishListSerializer, CartSerializer


@extend_schema(request=WishListSerializer)
@api_view(['GET', 'POST'])
def wish_list_by_user(request, userId):
    if request.method == 'POST':
        serializer = WishListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Wishlist item created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        wishlist = Wishlist.objects.filter(user=userId)
        serializer = WishListSerializer(wishlist, many=True)
        return Response(serializer.data)

    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['GET', 'POST'])
def cart_list_by_user(request, userId):
    if request.method == 'POST':
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Cart item added successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        cart_items = Cart.objects.filter(user=userId)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def orderHistoryByUserId(request):
    pass

'''
    Transaction code is implemented here
'''







