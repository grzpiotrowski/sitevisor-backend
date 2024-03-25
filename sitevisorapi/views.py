from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .models import Issue, Room, Sensor, Project, SensorType
from .serializers import IssueSerializer, RoomSerializer, SensorSerializer, ProjectSerializer, SensorTypeSerializer, UserRegistrationSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import HttpResponse
import requests
from django.conf import settings

class SensorTypeViewSet(viewsets.ModelViewSet):
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset

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

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        return queryset

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        sensor_type = self.request.query_params.get('type')

        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
        
        if sensor_type is not None:
            queryset = queryset.filter(type=sensor_type)

        return queryset

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(owner=user)
    
class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def assign(self, request, pk=None):
        issue = self.get_object()
        assignee = User.objects.get(username=request.data.get('username'))
        issue.assignee = assignee
        issue.save()
        return Response({'status': 'issue assigned'})

class RegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    model = User
    permission_classes = [AllowAny]


class KafkaBridgeProxy(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        kafka_bridge_url = settings.KAFKA_BRIDGE_URL + "/topics"
        headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}

        # Forward the request to the Kafka Bridge
        response = requests.get(kafka_bridge_url, headers=headers)

        # Return the Kafka Bridge's response
        return HttpResponse(response.content, content_type=response.headers['Content-Type'], status=response.status_code)