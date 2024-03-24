from django.test import TestCase
from django.contrib.auth.models import User
from ..serializers import ProjectSerializer, RoomSerializer, SensorSerializer, PointSerializer, SensorTypeSerializer
from ..models import Project, Room, Point, Sensor, SensorType

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
