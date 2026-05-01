"""
Serializers for Blood Donation API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, BloodRequest, Donation, Notification, BloodInventory, ContactMessage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_eligible = serializers.BooleanField(read_only=True)
    next_eligible_date = serializers.DateField(read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'blood_group', 'phone', 'city', 'state',
            'date_of_birth', 'last_donation_date', 'is_available',
            'total_donations', 'is_eligible', 'next_eligible_date', 'age',
            'created_at', 'updated_at'
        ]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    blood_group = serializers.ChoiceField(choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ])
    phone = serializers.CharField(max_length=15)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        UserProfile.objects.create(
            user=user,
            blood_group=validated_data['blood_group'],
            phone=validated_data['phone'],
            city=validated_data['city'],
            state=validated_data['state'],
            date_of_birth=validated_data.get('date_of_birth'),
        )
        return user


class BloodRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.SerializerMethodField()

    class Meta:
        model = BloodRequest
        fields = [
            'id', 'requester', 'requester_name', 'patient_name',
            'blood_group_needed', 'units_needed', 'hospital_name',
            'city', 'state', 'contact_number', 'urgency', 'status',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['requester', 'created_at', 'updated_at']

    def get_requester_name(self, obj):
        return obj.requester.get_full_name() or obj.requester.username


class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = [
            'id', 'donor', 'donor_name', 'blood_request', 'donation_date',
            'units', 'blood_group', 'hospital_name', 'notes', 'created_at'
        ]
        read_only_fields = ['donor', 'created_at']

    def get_donor_name(self, obj):
        return obj.donor.get_full_name() or obj.donor.username


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'created_at']
        read_only_fields = ['created_at']


class BloodInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodInventory
        fields = ['id', 'blood_group', 'units_available', 'last_updated']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['created_at']
