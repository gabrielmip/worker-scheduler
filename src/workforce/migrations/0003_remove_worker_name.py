# Generated by Django 3.0.4 on 2020-03-31 01:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0002_worker_auth_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='worker',
            name='name',
        ),
    ]
