from rest_framework import serializers
from .models import Room, Sensor

class RoomSerializer(serializers.ModelSerializer):
    point1 = serializers.SerializerMethodField()
    point2 = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['name', 'level', 'color', 'opacity', 'point1', 'point2', 'height']

    def get_point1(self, obj):
        return {'x': obj.point1_x, 'y': obj.point1_y, 'z': obj.point1_z}

    def get_point2(self, obj):
        return {'x': obj.point2_x, 'y': obj.point2_y, 'z': obj.point2_z}

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'