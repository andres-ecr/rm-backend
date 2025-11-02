from django.db import migrations
from django.contrib.auth.hashers import make_password

def forward_func(apps, schema_editor):
    Client = apps.get_model("routes", "Client")
    User = apps.get_model("auth", "User")
    for client in Client.objects.all():
        if not client.user:
            username = f"client_{client.id}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'password': make_password("changeme")}
            )
            if not created:
                # If user already exists, create a unique username
                i = 1
                while True:
                    new_username = f"{username}_{i}"
                    if not User.objects.filter(username=new_username).exists():
                        user = User.objects.create(
                            username=new_username,
                            password=make_password("changeme")
                        )
                        break
                    i += 1
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
        ('routes', '0008_client_user'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]

