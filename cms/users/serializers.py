from rest_framework import serializers
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomUser
        fields = ('id','username','email','first_name','last_name','other_name', 'occupation','bio', 'profile_picture')


