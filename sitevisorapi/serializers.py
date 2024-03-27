from rest_framework import serializers
from .models import Issue, Room, Sensor, Project, Point, SensorType
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'x', 'y', 'z']

class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = ['id', 'name', 'project']

class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = ['id', 'name', 'project']

class SensorSerializer(serializers.ModelSerializer):
    # For creating a sensor, accept a SensorType ID
    type_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=SensorType.objects.all(),
        source='type'
    )
    
    # For reading sensor data, return the whole SensorType object
    type = SensorTypeSerializer(read_only=True)
    position = PointSerializer()
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Sensor
        fields = ['id', 'name', 'device_id', 'project', 'level', 'type', 'type_id', 'position', 'room']

    def create(self, validated_data):
        position_data = validated_data.pop('position')

        position = Point.objects.create(**position_data)
        sensor = Sensor.objects.create(**validated_data, position=position)
        return sensor

    def update(self, instance, validated_data):
        sensor_type = validated_data.pop('type', None)

        if sensor_type:
            # Ensure the sensor_type is an instance of SensorType
            if not isinstance(sensor_type, SensorType):
                raise ValidationError({'type_id': ['Invalid sensor type.']})
            instance.type = sensor_type

        # Handle position update if provided
        position_data = validated_data.pop('position', None)
        if position_data:
            for attr, value in position_data.items():
                setattr(instance.position, attr, value)
            instance.position.save()

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class RoomSerializer(serializers.ModelSerializer):
    point1 = PointSerializer()
    point2 = PointSerializer()
    sensors = SensorSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'project', 'level', 'color', 'opacity', 'point1', 'point2', 'height', 'sensors']

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
        # Handle point1 update if provided
        point1_data = validated_data.pop('point1', None)
        if point1_data:
            for attr, value in point1_data.items():
                setattr(instance.point1, attr, value)
            instance.point1.save()

        # Handle point2 update if provided
        point2_data = validated_data.pop('point2', None)
        if point2_data:
            for attr, value in point2_data.items():
                setattr(instance.point2, attr, value)
            instance.point2.save()

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class IssueSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')
    assignee = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), required=False, allow_null=True)
    object_id = serializers.IntegerField()
    object_type = serializers.SerializerMethodField()

    def get_object_type(self, obj):
        # Return name of the model for the related object.
        return obj.content_type.model    

    def to_internal_value(self, data):
        # Convert the model name string in 'object_type' to a ContentType instance.
        # Call the superclass method to ensure other validations are still run
        validated_data = super().to_internal_value(data)
        
        model_name = data.get('object_type')
        
        # Fetch the ContentType object for the given model name
        try:
            app_label = 'sitevisorapi'
            content_type = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        except ContentType.DoesNotExist:
            raise ValidationError({'object_type': [f'Invalid object type: {model_name}']})
        
        # Set the content_type in the validated_data
        validated_data['content_type'] = content_type

        return validated_data

    def create(self, validated_data):
        # Remove 'object_type' from validated_data
        validated_data.pop('object_type', None)
        return Issue.objects.create(**validated_data)

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'status', 'created_at', 'updated_at', 'creator', 'assignee', 'object_type', 'object_id', 'project']


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