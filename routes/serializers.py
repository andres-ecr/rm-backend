from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, CheckpointScan, Checkpoint, RouteRun, GuardAssignment, Route, UserProfile, Incident, Occurrence

class ClientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Client
        fields = ['id', 'name', 'is_active', 'username', 'password']
        read_only_fields = ['id', 'is_active']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        user = User.objects.create_user(username=username, password=password)
        client = Client.objects.create(user=user, **validated_data)
        return client

class UserProfileSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['is_admin', 'client']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'is_staff', 'profile']
        read_only_fields = ['is_staff']

    def create(self, validated_data):
        profile_data = validated_data.pop('userprofile', None)
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('userprofile', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()

        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if hasattr(instance, 'userprofile'):
            representation['profile'] = UserProfileSerializer(instance.userprofile).data
        return representation

class CheckpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkpoint
        fields = ['id', 'name', 'qr_code', 'order']

class RouteSerializer(serializers.ModelSerializer):
    checkpoints = CheckpointSerializer(many=True)
    client = ClientSerializer(read_only=True)
    client_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Route
        fields = ['id', 'name', 'checkpoints', 'client', 'client_id']

    def create(self, validated_data):
        checkpoints_data = validated_data.pop('checkpoints')
        client_id = validated_data.pop('client_id')
        client = Client.objects.get(id=client_id)
        route = Route.objects.create(client=client, name=validated_data['name'])
        for checkpoint_data in checkpoints_data:
            Checkpoint.objects.create(route=route, **checkpoint_data)
        return route

class CheckpointScanSerializer(serializers.ModelSerializer):
    checkpoint_name = serializers.CharField(source='checkpoint.name', read_only=True)
    qr_code = serializers.CharField(source='checkpoint.qr_code', read_only=True)

    class Meta:
        model = CheckpointScan
        fields = ['id', 'checkpoint_name', 'qr_code', 'scanned_at']

class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['id', 'description', 'timestamp']

class RouteRunSerializer(serializers.ModelSerializer):
    checkpoint_scans = serializers.SerializerMethodField()
    incidents = serializers.SerializerMethodField()

    class Meta:
        model = RouteRun
        fields = ['id', 'start_time', 'end_time', 'completed', 'checkpoint_scans', 'incidents']

    def get_checkpoint_scans(self, obj):
        # Limit to the latest 5 scans
        latest_scans = obj.checkpoint_scans.order_by('-scanned_at')[:5]
        return CheckpointScanSerializer(latest_scans, many=True).data

    def get_incidents(self, obj):
        # Limit to the latest 5 incidents
        latest_incidents = obj.incidents.order_by('-timestamp')[:5]
        return IncidentSerializer(latest_incidents, many=True).data

class GuardAssignmentSerializer(serializers.ModelSerializer):
    guard = serializers.SerializerMethodField()
    route = RouteSerializer(read_only=True)
    active_run = serializers.SerializerMethodField()

    class Meta:
        model = GuardAssignment
        fields = ['id', 'guard', 'route', 'shift', 'active_run']

    def get_guard(self, obj):
        return {
            'id': obj.guard.id,
            'username': obj.guard.username,
            'first_name': obj.guard.first_name,
            'last_name': obj.guard.last_name,
            'is_staff': obj.guard.is_staff,
            'profile': UserProfileSerializer(obj.guard.userprofile).data if hasattr(obj.guard, 'userprofile') else None
        }

    def get_active_run(self, obj):
        active_run = obj.route_runs.filter(completed=False).first()
        if active_run:
            return RouteRunSerializer(active_run).data
        return None

class AssignmentCheckpointScanSerializer(serializers.ModelSerializer):
    checkpoint_name = serializers.CharField(source='checkpoint.name', read_only=True)
    qr_code = serializers.CharField(source='checkpoint.qr_code', read_only=True)

    class Meta:
        model = CheckpointScan
        fields = ['id', 'checkpoint_name', 'qr_code', 'scanned_at']

class AssignmentRouteRunSerializer(serializers.ModelSerializer):
    latest_scan = serializers.SerializerMethodField()

    class Meta:
        model = RouteRun
        fields = ['id', 'start_time', 'end_time', 'completed', 'latest_scan']

    def get_latest_scan(self, obj):
        latest_scan = obj.checkpoint_scans.order_by('-scanned_at').first()
        if latest_scan:
            return AssignmentCheckpointScanSerializer(latest_scan).data
        return None

class OptimizedGuardAssignmentSerializer(serializers.ModelSerializer):
    guard = serializers.SerializerMethodField()
    route = RouteSerializer(read_only=True)
    active_run = serializers.SerializerMethodField()

    class Meta:
        model = GuardAssignment
        fields = ['id', 'guard', 'route', 'shift', 'active_run']

    def get_guard(self, obj):
        return {
            'id': obj.guard.id,
            'username': obj.guard.username,
            'first_name': obj.guard.first_name,
            'last_name': obj.guard.last_name,
            'is_staff': obj.guard.is_staff,
            'profile': UserProfileSerializer(obj.guard.userprofile).data if hasattr(obj.guard, 'userprofile') else None
        }

    def get_active_run(self, obj):
        active_run = obj.route_runs.filter(completed=False).first()
        if active_run:
            return AssignmentRouteRunSerializer(active_run).data
        return None

class ReportCheckpointScanSerializer(serializers.ModelSerializer):
    checkpoint_name = serializers.CharField(source='checkpoint.name', read_only=True)
    qr_code = serializers.CharField(source='checkpoint.qr_code', read_only=True)

    class Meta:
        model = CheckpointScan
        fields = ['id', 'checkpoint_name', 'qr_code', 'scanned_at']

class OccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occurrence
        fields = ['id', 'occurrence_type', 'name', 'dni', 'motive', 'observation', 'remission_guide', 'bill', 'timestamp', 'driver_name', 'car_plate']

class ReportRouteRunSerializer(serializers.ModelSerializer):
    checkpoint_scans = ReportCheckpointScanSerializer(many=True, read_only=True)
    incidents = IncidentSerializer(many=True, read_only=True)
    occurrences = OccurrenceSerializer(many=True, read_only=True)

    class Meta:
        model = RouteRun
        fields = ['id', 'start_time', 'end_time', 'completed', 'checkpoint_scans', 'incidents', 'occurrences']

