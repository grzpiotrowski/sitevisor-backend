from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Room, Sensor
from .serializers import RoomSerializer, SensorSerializer, UserRegistrationSerializer
from django.contrib.auth.models import User

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]

class RegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    model = User
    permission_classes = [AllowAny]
