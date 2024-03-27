from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Project(models.Model):
    name = models.CharField(max_length=255)
    kafka_topics = models.CharField(max_length=1024, blank=True, default='')
    owner = models.ForeignKey(User, related_name='owned_projects', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Point(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    def __str__(self):
        return  f'({self.x}, {self.y}, {self.z})'

class SensorType(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, related_name='sensor_types', on_delete=models.CASCADE)

    class Meta:
        # Composite unique constraint
        unique_together = ('name', 'project')

    def __str__(self):
        return f'{self.project.name} - {self.name}'

class Room(models.Model):
    name = models.CharField(max_length=255)
    level = models.IntegerField()
    color = models.IntegerField()
    opacity = models.FloatField()
    point1 = models.ForeignKey(Point, related_name='room_point1', on_delete=models.CASCADE)
    point2 = models.ForeignKey(Point, related_name='room_point2', on_delete=models.CASCADE)
    height = models.FloatField(default=3)
    project = models.ForeignKey(Project, related_name='rooms', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Sensor(models.Model):
    name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    level = models.IntegerField()
    type = models.ForeignKey(SensorType, on_delete=models.CASCADE, related_name='sensors')
    position = models.ForeignKey(Point, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='sensors', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Issue(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=100, default='open')  # open, in progress, resolved
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name='created_issues', on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, related_name='assigned_issues', null=True, blank=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(Project, related_name='issues', on_delete=models.CASCADE)
    # Relation fields to associate with any object - sensor, room etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.title