# Generated by Django 3.2.7 on 2021-09-25 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0007_auto_20210919_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workevent',
            name='canceled_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='Data cancelamento'),
        ),
        migrations.AlterField(
            model_name='workevent',
            name='created_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Data criaçã0'),
        ),
        migrations.AlterField(
            model_name='workevent',
            name='event_id',
            field=models.AutoField(primary_key=True, serialize=False, unique=True),
        ),
    ]
