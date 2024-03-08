from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Project, Room, Point, Sensor

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='homer', password='secret123')
        self.project = Project.objects.create(name='Homer Project', owner=self.user)
        self.point1 = Point.objects.create(x=4.0, y=0.0, z=9.0)
        self.point2 = Point.objects.create(x=-1.0, y=0.0, z=-1.0)
        self.sensorPosition = Point.objects.create(x=1.0, y=0.0, z=-3.5)
        self.room = Room.objects.create(name='Living Room', level=1, color=0xFFFFFF, opacity=0.7, point1=self.point1, point2=self.point2, project=self.project)
        self.sensor = Sensor.objects.create(name='Thermometer', level=1, position=self.point1, project=self.project)

    def test_models_str(self):
        self.assertEqual(str(self.project), 'Homer Project')
        self.assertEqual(str(self.room), 'Living Room')
        self.assertEqual(str(self.sensor), 'Thermometer')
