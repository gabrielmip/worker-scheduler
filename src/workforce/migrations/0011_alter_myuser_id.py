# Generated by Django 3.2.7 on 2021-09-26 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0010_auto_20210926_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
