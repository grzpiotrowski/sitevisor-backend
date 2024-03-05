from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Room, Sensor, Project
from .serializers import RoomSerializer, SensorSerializer, ProjectSerializer, UserRegistrationSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Working on the copy of a request to avoid error: This QueryDict instance is immutable
        mutable_data = request.data.copy()
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

class RegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    model = User
    permission_classes = [AllowAny]
