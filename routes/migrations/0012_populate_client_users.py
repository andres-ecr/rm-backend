from django.db import migrations
from django.contrib.auth.hashers import make_password

def forward_func(apps, schema_editor):
    Client = apps.get_model("routes", "Client")
    User = apps.get_model("auth", "User")
    for client in Client.objects.all():
        if not client.user:
            base_username = f"client_{client.id}"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            user = User.objects.create(
                username=username,
                password=make_password("changeme")
            )
            client.user = user
            client.save()

def reverse_func(apps, schema_editor):
    Client = apps.get_model("routes", "Client")
    User = apps.get_model("auth", "User")
    for client in Client.objects.all():
        if client.user:
            user = client.user
            client.user = None
            client.save()
            user.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0011_add_user_to_client'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]

