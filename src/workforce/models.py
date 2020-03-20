from django.db import models


class Calendar(models.Model):
    calendar_id = models.CharField(max_length=200, unique=True, primary_key=True)


class Worker(models.Model):
    name = models.CharField(max_length=200)
    calendar = models.ForeignKey(Calendar, null=True, on_delete=models.SET_NULL)
