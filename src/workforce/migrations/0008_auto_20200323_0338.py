# Generated by Django 3.0.4 on 2020-03-23 03:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0007_auto_20200323_0221'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(max_length=200, verbose_name='Google agenda event ID')),
                ('name', models.CharField(max_length=200)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workforce.Calendar')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workforce.User')),
            ],
        ),
        migrations.DeleteModel(
            name='WorkEvents',
        ),
    ]