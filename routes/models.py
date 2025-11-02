from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {'Admin' if self.is_admin else 'Guard'} - {self.client.name if self.client else 'No Client'}"

class Route(models.Model):
    name = models.CharField(max_length=100)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.client.name}"

class GuardAssignment(models.Model):
    SHIFT_CHOICES = [
        ('day', 'Día'),
        ('night', 'Noche'),
        ('weekend', 'Fin de semana'),
    ]

    route = models.ForeignKey(Route, related_name='guard_assignments', on_delete=models.CASCADE)
    guard = models.OneToOneField(User, related_name='route_assignment', on_delete=models.CASCADE)
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)

    @property
    def active_run(self):
        return self.route_runs.filter(completed=False).first()

    @property
    def last_completed_run(self):
        return self.route_runs.filter(completed=True).order_by('-end_time').first()

    class Meta:
        indexes = [
            models.Index(fields=['guard']),
            models.Index(fields=['route']),
        ]

    def __str__(self):
        return f"{self.guard.username} - {self.route.name} ({self.get_shift_display()})"

class RouteRun(models.Model):
    assignment = models.ForeignKey(GuardAssignment, related_name='route_runs', on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['assignment', 'completed']),
            models.Index(fields=['start_time']),
        ]

    @property
    def incidents(self):
        return self.incident_set.all()

    def mark_as_completed(self):
        self.end_time = timezone.now()
        self.completed = True
        self.save()

    def __str__(self):
        return f"Recorrido de {self.assignment.guard.username} - {self.assignment.route.name} - {self.start_time}"

class Checkpoint(models.Model):
    route = models.ForeignKey(Route, related_name='checkpoints', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    qr_code = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['route', 'order']),
            models.Index(fields=['qr_code']),
        ]

    def __str__(self):
        return f"{self.route.name} - {self.name} (Orden: {self.order})"

class CheckpointScan(models.Model):
    checkpoint = models.ForeignKey(Checkpoint, related_name='scans', on_delete=models.CASCADE)
    route_run = models.ForeignKey(RouteRun, related_name='checkpoint_scans', on_delete=models.CASCADE)
    scanned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('checkpoint', 'route_run')
        indexes = [
            models.Index(fields=['route_run', 'scanned_at']),
        ]

    def __str__(self):
        return f"{self.checkpoint.name} - {self.route_run} - {self.scanned_at}"

class Incident(models.Model):
    guard = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents')
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    route_run = models.ForeignKey(RouteRun, on_delete=models.CASCADE, related_name='incidents', null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['guard', 'timestamp']),
            models.Index(fields=['route_run']),
        ]

    def __str__(self):
        return f"Incident by {self.guard.username} at {self.timestamp}"

class Occurrence(models.Model):
    OCCURRENCE_TYPES = [
        ('person', 'Person'),
        ('car', 'Car'),
    ]

    route_run = models.ForeignKey(RouteRun, on_delete=models.CASCADE, related_name='occurrences')
    occurrence_type = models.CharField(max_length=10, choices=OCCURRENCE_TYPES)
    name = models.CharField(max_length=100)
    dni = models.CharField(max_length=20)
    motive = models.TextField()
    observation = models.TextField(blank=True, null=True)
    remission_guide = models.CharField(max_length=100, blank=True, null=True)
    bill = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    # Additional fields for car occurrences
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    car_plate = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.get_occurrence_type_display()} Occurrence - {self.name}"

    class Meta:
        indexes = [
            models.Index(fields=['route_run', 'occurrence_type']),
            models.Index(fields=['timestamp']),
        ]

# Signal handlers for creating UserProfiles for superusers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        UserProfile.objects.create(user=instance, is_admin=True)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_superuser and not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance, is_admin=True)

