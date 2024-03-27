from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from ..models import Project, SensorType, Room, Sensor, Point, Issue

class ViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='homer', password='secret123')
        self.project = Project.objects.create(name='Homer Project', owner=self.user)
        self.sensorType = SensorType.objects.create(name="Temperature", project=self.project)
        self.sensorType2 = SensorType.objects.create(name="Vibration", project=self.project)
        # Setup points for rooms and sensors
        self.point1 = Point.objects.create(x=4.0, y=0.0, z=9.0)
        self.point2 = Point.objects.create(x=-1.0, y=0.0, z=-1.0)
        self.sensorPosition = Point.objects.create(x=1.0, y=0.0, z=-3.5)

        self.sensor = Sensor.objects.create(
            name='Thermometer', 
            device_id='sensor-123', 
            level=1, 
            type=self.sensorType, 
            position=self.sensorPosition, 
            project=self.project
        )

        self.sensor2 = Sensor.objects.create(
            name='Shake-o-meter', 
            device_id='sensor-456', 
            level=0, 
            type=self.sensorType2, 
            position=self.point1, 
            project=self.project
        )

        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        url = reverse('project-list')
        data = {'name': 'New Project', 'kafka_topics': 'topic1', 'owner': self.user.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.last().name, 'New Project')

    def test_list_projects(self):
        url = reverse('project-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one project owned by `homer`

    def test_create_sensor_type(self):
        url = reverse('sensortype-list')
        initialSensorTypeCount = SensorType.objects.count()
        data = {'name': 'Humidity', 'project': self.project.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SensorType.objects.count(), initialSensorTypeCount+1)
        self.assertEqual(SensorType.objects.last().name, 'Humidity')

    def test_create_room(self):
        url = reverse('room-list')
        data = {
            'name': 'Living Room',
            'project': self.project.id,
            'level': 1,
            'color': 0xFFFFFF,
            'opacity': 0.5,
            'point1': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'point2': {'x': 5.0, 'y': 5.0, 'z': 3.0},
            'height': 2.5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)
        self.assertEqual(Room.objects.get().name, 'Living Room')

    def test_create_sensor(self):
        url = reverse('sensor-list')
        initialSensorCount = Sensor.objects.count()
        data = {
            'name': 'New Thermometer',
            'device_id': 'dev-123',
            'project': self.project.id,
            'level': 1,
            'type_id': self.sensorType.id,
            'position': {'x': 1.0, 'y': 0.0, 'z': -3.5}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sensor.objects.count(), initialSensorCount+1)
        new_sensor_exists = Sensor.objects.filter(name='New Thermometer').exists()
        self.assertTrue(new_sensor_exists)

    def test_filter_sensors_by_type(self):
        url = reverse('sensor-list') + f'?project_id={self.project.id}&type={self.sensorType.id}'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming there is at least one sensor of the type `Temperature`
        self.assertTrue(any(sensor['type']['id'] == self.sensorType.id for sensor in response.data))
        self.assertFalse(any(sensor['type']['id'] == self.sensorType2.id for sensor in response.data))

class IssueViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='homer', password='secret123')
        self.user2 = User.objects.create_user(username='marge', password='secret456')
        self.project = Project.objects.create(name='The Simpsons Project', owner=self.user)
        self.point = Point.objects.create(x=5.0, y=5.0, z=5.0)
        self.room = Room.objects.create(name='Living Room', level=1, color=0xFFFFFF, opacity=0.5, point1=self.point, point2=self.point, project=self.project)
        self.sensorType = SensorType.objects.create(name="Temperature", project=self.project)
        self.sensorType2 = SensorType.objects.create(name="Vibration", project=self.project)
        self.sensor = Sensor.objects.create(name='Temp Sensor', device_id='temp-001', level=0, type=self.sensorType, position=self.point, project=self.project)

        self.issue1 = Issue.objects.create(title='Issue 1', description='First Issue', project=self.project, content_object=self.room, creator=self.user)
        self.issue2 = Issue.objects.create(title='Issue 2', description='Second Issue', project=self.project, content_object=self.sensor, creator=self.user2)

        self.client.force_authenticate(user=self.user)

    def test_create_issue(self):
        url = reverse('issue-list')
        data = {
            'title': 'New Issue',
            'description': 'Something went horribly wrong with this project',
            'project': self.project.id,
            'object_id': self.room.id,
            'object_type': 'room'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Issue.objects.count(), 3)
        self.assertEqual(Issue.objects.filter(creator=self.user).count(), 2)

    def test_filter_issues_by_project(self):
        url = reverse('issue-list') + f'?project_id={self.project.id}'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_assign_issue(self):
        url = reverse('issue-assign', kwargs={'pk': self.issue1.pk})
        data = {'username': 'marge'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.issue1.refresh_from_db()
        self.assertEqual(self.issue1.assignee, self.user2)

    def test_filter_issues_by_assignee(self):
        # First, assign issue2 to user2
        self.issue2.assignee = self.user2
        self.issue2.save()

        # Filter issues by assignee (user2)
        url = reverse('issue-list') + '?assignee=marge'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
