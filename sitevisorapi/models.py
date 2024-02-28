from django.db import models

class Point(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

class Room(models.Model):
    name = models.CharField(max_length=255)
    level = models.IntegerField()
    opacity = models.FloatField()
    point1 = models.ForeignKey(Point, related_name='room_point1', on_delete=models.CASCADE)
    point2 = models.ForeignKey(Point, related_name='room_point2', on_delete=models.CASCADE)
    height = models.FloatField(default=3)

    def __str__(self):
        return self.name

class Sensor(models.Model):
    name = models.CharField(max_length=255)
    level = models.IntegerField()
    position = models.ForeignKey(Point, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
