from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

import requests

from .models import CustomUser, City

class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        style={'input_type': 'confirm_password'},
        write_only=True,
        min_length=4
    )
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        } 

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class CityOutputSerializer(serializers.ModelSerializer):
    temperature = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['name', 'lat', 'lon', 'temperature']

    def get_temperature(self, obj):
        cache_key = f"city_temp_{obj.id}"
        cached_temp = cache.get(cache_key)
        
        if cached_temp is not None:
            return cached_temp
            
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={obj.lat}&longitude={obj.lon}&current_weather=true"
            response = requests.get(url, timeout=3).json()
            temp = response.get('current_weather', {}).get('temperature')
            
            if temp is not None:
                cache.set(cache_key, temp, timeout=900) 
                
            return temp
        except Exception:
            return None

class CityInputSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=100)

class MailingTimeSerializer(serializers.Serializer):
    time = serializers.TimeField(required=True)