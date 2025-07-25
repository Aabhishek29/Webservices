from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import SendOTPSerializer, VerifyOTPSerializer, UserUpdateSerializer, AddAddressSerializer
from .models import Users

def home(request):
    return HttpResponse("<h1>Hello world</h1>")


@extend_schema(request=SendOTPSerializer)
@api_view(['POST'])
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.send_otp()
        return Response({'message': 'OTP sent successfully'})
    else:
        return Response(serializer.errors, status=400)



@extend_schema(request=VerifyOTPSerializer)
@api_view(['POST'])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=200)
    else:
        return Response(serializer.errors, status=400)





@extend_schema(
    request=UserUpdateSerializer,
    examples=[
        OpenApiExample(
            "Example payload",
            value={
                "userId": "eb951e75-c19b-4b91-935e-xxxxxx",
                "firstName": "Tony",
                "lastName": "Stark",
                "email": "example@mail.com"
            },
            request_only=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_by_userId(request):
    try:
        user_id = request.data.get('userId')
        if not user_id:
            return Response({'message': 'userId is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Users.objects.get(userId=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': 'Something went wrong', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@extend_schema(request=AddAddressSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_address(request):
    serializer = AddAddressSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Address added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)