from rest_framework import serializers
from .models import Users, Addresses, SubscriberModel
import random
from .utils import sendOTPForMobile, send_successfully_account_created_sms
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

        send_successfully_account_created_sms(user.phoneNumber)
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



class SubscriberSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    userEmail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SubscriberModel
        fields = [
            'subscriberId',
            'email',
            'userId',
            'userEmail',
            'createdAt',
            'updatedAt'
        ]
        read_only_fields = ['subscriberId', 'createdAt', 'updatedAt', 'userEmail']

    def get_userEmail(self, obj):
        return obj.user.email if obj.user else None

    def create(self, validated_data):
        user_id = validated_data.pop('userId', None)
        user = None

        if user_id:
            try:
                user = Users.objects.get(pk=user_id)
            except Users.DoesNotExist:
                raise serializers.ValidationError({"userId": "User with this ID does not exist."})

        return SubscriberModel.objects.create(user=user, **validated_data)