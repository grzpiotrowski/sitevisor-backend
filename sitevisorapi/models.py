from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=255)
    level = models.IntegerField()
    color = models.BigIntegerField()
    opacity = models.FloatField()
    point1_x = models.FloatField()
    point1_y = models.FloatField()
    point1_z = models.FloatField()
    point2_x = models.FloatField()
    point2_y = models.FloatField()
    point2_z = models.FloatField()
    height = models.FloatField(default=3)

    def __str__(self):
        return self.name
