from django.test import TestCase
from django.contrib.auth.models import User
from ..serializers import ProjectSerializer
from ..models import Project

class SerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='homer', password='secret123')
        self.project = Project.objects.create(name='Homer Project', owner=self.user)

    def test_project_serializer(self):
        project_data = ProjectSerializer(instance=self.project).data
        expected_keys = {'id', 'name', 'kafka_topics', 'owner', 'rooms', 'sensors'}
        self.assertEqual(set(project_data.keys()), expected_keys)