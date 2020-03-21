from django.db import models


class Calendar(models.Model):
    def __str__(self):
        return self.name

    calendar_id = models.CharField(max_length=200, unique=True, primary_key=True)
    name = models.CharField(max_length=200, default="")


class Worker(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=200)
    calendar = models.ForeignKey(Calendar, null=True, on_delete=models.SET_NULL)
