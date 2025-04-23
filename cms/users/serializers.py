from rest_framework import serializers
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomUser
        fields = ('id','username','email','first_name','last_name','other_name', 'occupation','bio', 'profile_picture')

class CustomUserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2','first_name','last_name','other_name', 'occupation','bio', 'profile_picture')
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match.")
        return data
    
    def create(self, validated_data):
        # Remove password2 before creating user
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user
