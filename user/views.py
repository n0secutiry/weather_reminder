from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import CityInputSerializer, UserRegisterSerializer, CityOutputSerializer
from .models import City

import requests

class UserRegisterView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CitySubscriprionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_cities = request.user.cities.all()
        serializer = CityOutputSerializer(user_cities, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        input_serializer = CityInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        city_name = input_serializer.validated_data['name']
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"

        try:
            geo_response = requests.get(geo_url, timeout=3).json()
            if not geo_response.get('results'):
                return Response({'error': 'City not found'}, status=status.HTTP_404_NOT_FOUND)
            
            city_data = geo_response['results'][0]
        except requests.RequestException:
            return Response({'error': 'Weather service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        city, created = City.objects.get_or_create(
            name=city_data['name'],
            defaults={
                'lat': city_data['latitude'],
                'lon': city_data['longitude']
            }
        )
        city.subscribers.add(request.user)

        output_serializer = CityOutputSerializer(city)
        return Response({
            "message": f"You subscribed to {city.name}",
            "city_details": output_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        city_name = request.data.get('name')
        
        if not city_name:
             return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            city = City.objects.get(name=city_name)
            city.subscribers.remove(request.user) 
            return Response({'successful': 'City unsubscribed.'}, status=status.HTTP_204_NO_CONTENT)
        except City.DoesNotExist:
            return Response({'error': 'City not found in DB'}, status=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request):
        interval = request.data.get('interval')
        webhook_url = request.data.get('webhook_url')
        allowed_intervals = [1, 6, 12, 24, 168]
        
        updated = False

        if interval is not None:
            try:
                interval = int(interval)
                if interval not in allowed_intervals:
                    return Response({'error': f'Invalid interval. Choose from {allowed_intervals}'}, status=status.HTTP_400_BAD_REQUEST)
                
                request.user.mailing_interval = interval
                updated = True
            except ValueError:
                return Response({'error': 'Interval must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        if webhook_url is not None:
            request.user.webhook_url = webhook_url
            updated = True

        if updated:
            request.user.save()
            return Response({'successful': 'User settings updated successfully!'}, status=status.HTTP_200_OK)

        return Response({'error': 'No valid fields provided to update'}, status=status.HTTP_400_BAD_REQUEST)