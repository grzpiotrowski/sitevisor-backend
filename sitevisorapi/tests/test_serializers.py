from django.test import TestCase
from django.contrib.auth.models import User
from ..serializers import ProjectSerializer, RoomSerializer, SensorSerializer, PointSerializer, SensorTypeSerializer, IssueSerializer
from ..models import Project, Room, Point, Sensor, SensorType, Issue
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

class SerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='homer', password='secret123')
        self.project = Project.objects.create(name='Homer Project', owner=self.user, kafka_topics='my_topic')
        self.sensorType = SensorType.objects.create(name='Temperature', project=self.project)
        # Setup points for rooms and sensors
        self.point1 = Point.objects.create(x=4.0, y=0.0, z=9.0)
        self.point2 = Point.objects.create(x=-1.0, y=0.0, z=-1.0)
        self.sensorPosition = Point.objects.create(x=1.0, y=0.0, z=-3.5)

        self.room = Room.objects.create(
            name='Living Room', 
            level=1, 
            color=0xFFFFFF, 
            opacity=0.7, 
            point1=self.point1, 
            point2=self.point2, 
            project=self.project,
            height=2.5
        )
        self.sensor = Sensor.objects.create(
            name='Thermometer', 
            device_id='sensor-123', 
            level=1, 
            type=self.sensorType, 
            position=self.sensorPosition, 
            project=self.project
        )

    def test_project_serializer(self):
        project_data = ProjectSerializer(instance=self.project).data
        expected_keys = {'id', 'name', 'kafka_topics', 'owner', 'rooms', 'sensors'}
        self.assertEqual(set(project_data.keys()), expected_keys)

    def test_point_serializer(self):
        point_data = PointSerializer(instance=self.point1).data
        expected_keys = {'id', 'x', 'y', 'z'}
        self.assertEqual(set(point_data.keys()), expected_keys)
        self.assertEqual(point_data['x'], self.point1.x)

    def test_sensor_type_serializer(self):
        sensor_type_data = SensorTypeSerializer(instance=self.sensorType).data
        expected_keys = {'id', 'name', 'project'}
        self.assertEqual(set(sensor_type_data.keys()), expected_keys)

    def test_room_serializer(self):
        room_data = RoomSerializer(instance=self.room).data
        expected_keys = {'id', 'name', 'project', 'level', 'color', 'opacity', 'point1', 'point2', 'height'}
        self.assertEqual(set(room_data.keys()), expected_keys)
        self.assertEqual(room_data['color'], '#ffffff')

    def test_sensor_serializer(self):
        sensor_data = SensorSerializer(instance=self.sensor).data
        expected_keys = {'id', 'name', 'device_id', 'project', 'level', 'type', 'position'}
        self.assertEqual(set(sensor_data.keys()), expected_keys)
        self.assertTrue('type_id' not in sensor_data)  # type_id is write-only
        self.assertEqual(sensor_data['type']['name'], 'Temperature')

    def test_room_serializer_creation(self):
        room_serializer = RoomSerializer(data={
            'name': 'Test Room', 
            'level': 1, 
            'color': '#ff0000', 
            'opacity': 0.5, 
            'point1': {'x': 4.0, 'y': 0.0, 'z': 9.0}, 
            'point2': {'x': -1.0, 'y': 0.0, 'z': -1.0},
            'project': self.project.id,
            'height': 3.0
        })
        self.assertTrue(room_serializer.is_valid(), room_serializer.errors)
        new_room = room_serializer.save()
        self.assertEqual(new_room.name, 'Test Room')
        self.assertEqual(new_room.color, 0xFF0000)

    def test_room_serializer_update_without_changing_points(self):
        updated_name = 'Updated Room Name'
        updated_opacity = 0.9
        room_serializer = RoomSerializer(instance=self.room, data={
            'name': updated_name,
            'opacity': updated_opacity,
            # Not providing new data for point1 and point2
        }, partial=True)
        self.assertTrue(room_serializer.is_valid(), room_serializer.errors)
        updated_room = room_serializer.save()
        self.assertEqual(updated_room.name, updated_name)
        self.assertEqual(updated_room.opacity, updated_opacity)
        # Verify that points remain unchanged
        self.assertEqual(updated_room.point1, self.point1)
        self.assertEqual(updated_room.point2, self.point2)

    def test_room_serializer_update_with_new_points(self):
        new_point1_data = {'x': 10.0, 'y': 20.0, 'z': 30.0}
        new_point2_data = {'x': -10.0, 'y': -20.0, 'z': -30.0}
        room_serializer = RoomSerializer(instance=self.room, data={
            'point1': new_point1_data,
            'point2': new_point2_data,
        }, partial=True)
        self.assertTrue(room_serializer.is_valid(), room_serializer.errors)
        updated_room = room_serializer.save()
        # Verify that points have been updated
        self.assertEqual(updated_room.point1.x, new_point1_data['x'])
        self.assertEqual(updated_room.point1.y, new_point1_data['y'])
        self.assertEqual(updated_room.point1.z, new_point1_data['z'])
        self.assertEqual(updated_room.point2.x, new_point2_data['x'])
        self.assertEqual(updated_room.point2.y, new_point2_data['y'])
        self.assertEqual(updated_room.point2.z, new_point2_data['z'])

    def test_sensor_serializer_creation(self):
        sensor_serializer = SensorSerializer(data={
            'name': 'New Sensor', 
            'device_id': 'sensor-456', 
            'level': 1, 
            'type_id': self.sensorType.id, 
            'position': {'x': 1.0, 'y': 0.0, 'z': -3.5}, 
            'project': self.project.id
        })
        self.assertTrue(sensor_serializer.is_valid(), sensor_serializer.errors)
        new_sensor = sensor_serializer.save()
        self.assertEqual(new_sensor.name, 'New Sensor')
        self.assertEqual(new_sensor.type, self.sensorType)

class IssueSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bart', password='secret123')
        self.project = Project.objects.create(name='Bart Project', owner=self.user, kafka_topics='my-topic')
        self.point = Point.objects.create(x=1.0, y=2.0, z=3.0)
        self.sensorType = SensorType.objects.create(name='Humidity', project=self.project)
        self.sensor = Sensor.objects.create(name='Humidity Sensor', device_id='sensor-001', level=1, type=self.sensorType, position=self.point, project=self.project)
        self.room = Room.objects.create(name='Conference Room', level=1, color=0xFFFFFF, opacity=0.5, point1=self.point, point2=self.point, project=self.project, height=2.5)

    def test_issue_serializer_serialization(self):
        issue = Issue.objects.create(title='Sensor Malfunction', description='A sensor is not working properly.', status='open', creator=self.user, content_object=self.sensor, project=self.project)
        serializer = IssueSerializer(instance=issue)
        data = serializer.data

        expected_fields = {'id', 'title', 'description', 'status', 'created_at', 'updated_at', 'creator', 'assignee', 'object_type', 'object_id', 'project'}
        self.assertEqual(set(data.keys()), expected_fields)
        self.assertEqual(data['title'], 'Sensor Malfunction')
        self.assertEqual(data['object_type'], 'sensor')

    def test_issue_serializer_deserialization_and_creation(self):
        issue_data = {
            'title': 'Room Temperature Issue',
            'description': 'The room is too cold.',
            'status': 'open',
            'object_type': 'room',
            'object_id': self.room.id,
            'project': self.project.id
        }

        # Directly testing the serializer's handling of valid data,
        # excluding the creator from the initial data since it's read-only
        serializer = IssueSerializer(data=issue_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        issue = serializer.save(creator=self.user)

        # Verifying the Issue instance was created correctly
        self.assertIsInstance(issue, Issue)
        self.assertEqual(issue.title, 'Room Temperature Issue')
        self.assertEqual(issue.content_object, self.room)
        self.assertEqual(issue.creator, self.user)

        # Verify the serialized representation includes the creator's username
        serialized_data = IssueSerializer(instance=issue).data
        self.assertEqual(serialized_data['creator'], self.user.username)

    def test_invalid_object_type(self):
        issue_data = {
            'title': 'Invalid Object Issue',
            'description': 'Trying to associate with an invalid object type.',
            'status': 'open',
            'object_type': 'invalidtype',
            'object_id': 1,
            'project': self.project.id
        }

        serializer = IssueSerializer(data=issue_data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertTrue('Invalid object type' in str(context.exception))

    def test_issue_creation_with_content_type(self):
        content_type = ContentType.objects.get_for_model(Sensor)
        issue_data = {
            'title': 'New Sensor Issue',
            'description': 'Issue related to a sensor.',
            'status': 'open',
            'object_id': self.sensor.id,
            'object_type': 'sensor',
            'project': self.project.id
        }

        serializer = IssueSerializer(data=issue_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        issue = serializer.save(creator=self.user)

        self.assertEqual(issue.content_object, self.sensor)