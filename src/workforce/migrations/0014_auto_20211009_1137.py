# Generated by Django 3.2.7 on 2021-10-09 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0013_alter_patient_auth_user'),
    ]

    operations = [
        migrations.operations.RunSQL(
            ''
            # 'alter table auth_user_user_permissions rename column user_id to myuser_id'
        )
    ]
