import uuid
from rest_framework import serializers
from .models import UserAccount

class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Include password field for writing only

    def create(self, validated_data):
        # Extract password from validated data
        password = validated_data.pop('password', None)
        # Create user instance without password
        user = UserAccount.objects.create(**validated_data)
        # Set password for the user and save
        if password:
            user.set_password(password)
            user.save()
        return user

    class Meta:
        model = UserAccount
        fields = '__all__'  # Use all fields from the model
        extra_kwargs = {'password': {'write_only': True}} 

# serializers.py

# serializers.py
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer

class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = UserAccount
        fields = ('id', 'username', 'email', 'password', 'name', 'phone_number', 'plan', 'auth_level', 'unique_uuid_user', 'dp')
        extra_kwargs = {'password': {'write_only': True}}

class CustomUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = UserAccount
        fields = ('id', 'username', 'email', 'name', 'phone_number', 'plan', 'auth_level', 'unique_uuid_user', 'dp')






