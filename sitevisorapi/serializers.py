from rest_framework import serializers
from .models import Room, Sensor, Point
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'x', 'y', 'z']

class RoomSerializer(serializers.ModelSerializer):
    point1 = PointSerializer()
    point2 = PointSerializer()

    class Meta:
        model = Room
        fields = ['id', 'name', 'level', 'color', 'opacity', 'point1', 'point2', 'height']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['color'] = f'#{instance.color:06x}'
        return ret

    def to_internal_value(self, data):
        if 'color' in data and isinstance(data['color'], str):
            data['color'] = int(data['color'].lstrip('#'), 16)
        return super().to_internal_value(data)

    def create(self, validated_data):
        point1_data = validated_data.pop('point1')
        point2_data = validated_data.pop('point2')
        point1 = Point.objects.create(**point1_data)
        point2 = Point.objects.create(**point2_data)
        room = Room.objects.create(**validated_data, point1=point1, point2=point2)
        return room

    def update(self, instance, validated_data):
        point1_data = validated_data.pop('point1')
        point2_data = validated_data.pop('point2')
        
        instance.name = validated_data.get('name', instance.name)
        instance.level = validated_data.get('level', instance.level)
        instance.color = validated_data.get('color', instance.color)
        instance.opacity = validated_data.get('opacity', instance.opacity)
        instance.height = validated_data.get('height', instance.height)

        # Update point1 and point2
        point1 = instance.point1
        point2 = instance.point2
        point1.x = point1_data.get('x', point1.x)
        point1.y = point1_data.get('y', point1.y)
        point1.z = point1_data.get('z', point1.z)
        point1.save()

        point2.x = point2_data.get('x', point2.x)
        point2.y = point2_data.get('y', point2.y)
        point2.z = point2_data.get('z', point2.z)
        point2.save()

        instance.save()
        return instance

class SensorSerializer(serializers.ModelSerializer):
    position = PointSerializer()

    class Meta:
        model = Sensor
        fields = ['id', 'name', 'level', 'position']

    def create(self, validated_data):
        position_data = validated_data.pop('position')
        position = Point.objects.create(**position_data)
        sensor = Sensor.objects.create(**validated_data, position=position)
        return sensor

    def update(self, instance, validated_data):
        position_data = validated_data.pop('position')
        
        instance.name = validated_data.get('name', instance.name)
        instance.level = validated_data.get('level', instance.level)

        # Update position
        position = instance.position
        position.x = position_data.get('x', position.x)
        position.y = position_data.get('y', position.y)
        position.z = position_data.get('z', position.z)
        position.save()

        instance.save()
        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user