from rest_framework import serializers
from .models import Users, Addresses, SubscriberModel
import random
from datetime import datetime, timedelta
from django.utils import timezone
from .utils import sendOTPForMobile, send_successfully_account_created_sms
from rest_framework_simplejwt.tokens import RefreshToken

class SendOTPSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(max_length=15)

    def validate_phoneNumber(self, value):
        """Validate phone number format"""
        # Remove any spaces or special characters
        cleaned = ''.join(filter(str.isdigit, value))
        if len(cleaned) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        return value

    def send_otp(self):
        phone = self.validated_data['phoneNumber']
        otp = str(random.randint(100000, 999999))

        # Get or create user with phone number only
        user, created = Users.objects.get_or_create(phoneNumber=phone)
        user.otp = otp
        user.otp_created_at = timezone.now()
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
            raise serializers.ValidationError({"error": "Invalid OTP or phone number"})

        # Check if OTP is expired (valid for 10 minutes)
        if user.otp_created_at:
            expiry_time = user.otp_created_at + timedelta(minutes=10)
            if timezone.now() > expiry_time:
                raise serializers.ValidationError({"error": "OTP has expired. Please request a new one."})

        # Mark verified and clear OTP
        user.is_verified = True
        user.otp = ''
        user.otp_created_at = None
        user.save()

        return {
            "userId": str(user.userId),
            "phoneNumber": user.phoneNumber,
            "is_new_user": not bool(user.password)  # If no password, user needs to complete signup
        }


class SignupSerializer(serializers.Serializer):
    """Complete signup after OTP verification"""
    phoneNumber = serializers.CharField(max_length=15)
    firstName = serializers.CharField(max_length=25, required=True)
    lastName = serializers.CharField(max_length=25, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6, required=True)

    def validate_phoneNumber(self, value):
        """Ensure user exists and is verified"""
        try:
            user = Users.objects.get(phoneNumber=value)
            if not user.is_verified:
                raise serializers.ValidationError("Phone number not verified. Please verify OTP first.")
            if user.password:
                raise serializers.ValidationError("User already exists. Please login instead.")
        except Users.DoesNotExist:
            raise serializers.ValidationError("Phone number not found. Please send OTP first.")
        return value

    def validate_email(self, value):
        """Check if email already exists"""
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        """Complete user signup with all details"""
        user = Users.objects.get(phoneNumber=validated_data['phoneNumber'])
        user.firstName = validated_data['firstName']
        user.lastName = validated_data['lastName']
        user.email = validated_data['email']
        user.set_password(validated_data['password'])  # Hash password
        user.save()

        # Send success SMS
        send_successfully_account_created_sms(user.phoneNumber)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "userId": str(user.userId),
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        }


class LoginSerializer(serializers.Serializer):
    """Login with phone number and password"""
    phoneNumber = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get('phoneNumber')
        password = data.get('password')

        try:
            user = Users.objects.get(phoneNumber=phone)
        except Users.DoesNotExist:
            raise serializers.ValidationError({"error": "Invalid phone number or password"})

        # Check if user has completed signup
        if not user.password:
            raise serializers.ValidationError({"error": "Please complete signup process first"})

        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError({"error": "Invalid phone number or password"})

        # Check if user is verified
        if not user.is_verified:
            raise serializers.ValidationError({"error": "Phone number not verified"})

        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError({"error": "Account is deactivated"})

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