from rest_framework import serializers
from .models import Users, Addresses
import random
from .utils import sendOTPForMobile
from rest_framework_simplejwt.tokens import RefreshToken

class SendOTPSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(max_length=15)

    def send_otp(self):
        phone = self.validated_data['phoneNumber']
        otp = str(random.randint(100000, 999999))

        user, created = Users.objects.get_or_create(phoneNumber=phone)
        user.otp = otp
        user.save()

        # Send OTP
        sendOTPForMobile(phone, otp)
        print(f"Sending OTP to {phone}: {otp}")

        return user


class VerifyOTPSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = Users.objects.get(phoneNumber=data['phoneNumber'], otp=data['otp'])
        except Users.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or phone number")

        # Mark verified and clear OTP
        user.is_verified = True
        user.otp = ''
        user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)



        return {
            "userId": str(user.userId),
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class UserUpdateSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField()  # Include if you update via userId
    firstName = serializers.CharField(required=False)
    lastName = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = Users
        fields = ['userId','firstName', 'lastName', 'email']



class AddAddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())  # uses userId

    class Meta:
        model = Addresses
        fields = ['user', 'locationName', 'streetAddress', 'city', 'state', 'postalCode', 'country']



