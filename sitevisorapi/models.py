from django.db import models
from django.contrib.auth.models import User

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
    position = models.ForeignKey(Point, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='sensors', on_delete=models.CASCADE)

    def __str__(self):
        return self.name