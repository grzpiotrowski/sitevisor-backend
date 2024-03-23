from rest_framework import serializers
from .models import Room, Sensor, Project, Point, SensorType
from django.contrib.auth.models import User

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'x', 'y', 'z']

class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = ['id', 'name', 'project']

class RoomSerializer(serializers.ModelSerializer):
    point1 = PointSerializer()
    point2 = PointSerializer()

    class Meta:
        model = Room
        fields = ['id', 'name', 'project', 'level', 'color', 'opacity', 'point1', 'point2', 'height']

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
    type = serializers.SlugRelatedField(slug_field='name', queryset=SensorType.objects.all())

    class Meta:
        model = Sensor
        fields = ['id', 'name', 'device_id', 'project', 'level', 'type', 'position']

    def create(self, validated_data):
        position_data = validated_data.pop('position')
        position = Point.objects.create(**position_data)
        sensor = Sensor.objects.create(**validated_data, position=position)
        return sensor

    def update(self, instance, validated_data):
        position_data = validated_data.pop('position')
        
        instance.name = validated_data.get('name', instance.name)
        instance.device_id = validated_data.get('device_id', instance.device_id)
        instance.level = validated_data.get('level', instance.level)
        instance.type = validated_data.get('type', instance.type)

        # Update position
        position = instance.position
        position.x = position_data.get('x', position.x)
        position.y = position_data.get('y', position.y)
        position.z = position_data.get('z', position.z)
        position.save()

        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    rooms = RoomSerializer(many=True, read_only=True)
    sensors = SensorSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'kafka_topics', 'owner', 'rooms', 'sensors']

    def create(self, validated_data):
        user = self.context['request'].user
        project = Project.objects.create(owner=user, **validated_data)
        return project

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