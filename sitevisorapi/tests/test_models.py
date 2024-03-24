from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Project, Room, Point, Sensor, SensorType

class ModelTestCase(TestCase):
    def setUp(self):
        # Setup user and project
        self.user = User.objects.create_user(username='homer', password='secret123')
        self.project = Project.objects.create(name='Homer Project', owner=self.user, kafka_topics='my_topic')
        
        # Setup points for rooms and sensors
        self.point1 = Point.objects.create(x=4.0, y=0.0, z=9.0)
        self.point2 = Point.objects.create(x=-1.0, y=0.0, z=-1.0)
        self.sensorPosition = Point.objects.create(x=1.0, y=0.0, z=-3.5)
        
        # Setup SensorType
        self.sensorType = SensorType.objects.create(name='Temperature', project=self.project)
        
        # Setup Room
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
        
        # Setup Sensor
        self.sensor = Sensor.objects.create(
            name='Thermometer', 
            device_id='sensor-123', 
            level=1, 
            position=self.sensorPosition, 
            project=self.project,
            type=self.sensorType
        )

    def test_project_str(self):
        self.assertEqual(str(self.project), 'Homer Project')

    def test_point_str(self):
        expected_str = f'({self.point1.x}, {self.point1.y}, {self.point1.z})'
        self.assertEqual(str(self.point1), expected_str)

    def test_sensor_type_str(self):
        self.assertEqual(str(self.sensorType), 'Homer Project - Temperature')

    def test_room_str(self):
        self.assertEqual(str(self.room), 'Living Room')

    def test_sensor_str(self):
        self.assertEqual(str(self.sensor), 'Thermometer')

    def test_room_color_hex_conversion(self):
        self.room.color = 0xFFAABB
        self.room.save()
        self.assertEqual(self.room.color, 0xFFAABB)

    def test_sensor_type_project_relationship(self):
        self.assertEqual(self.sensorType.project, self.project)
        self.assertTrue(self.project.sensor_types.filter(name='Temperature').exists())

    def test_sensor_project_relationship(self):
        self.assertEqual(self.sensor.project, self.project)
        self.assertTrue(self.project.sensors.filter(name='Thermometer').exists())

    def test_sensor_position_relationship(self):
        self.assertEqual(self.sensor.position, self.sensorPosition)

    def test_room_points_relationship(self):
        self.assertEqual(self.room.point1, self.point1)
        self.assertEqual(self.room.point2, self.point2)
