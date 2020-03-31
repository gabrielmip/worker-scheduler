import arrow
from django.db import models
from django.utils.translation import gettext_lazy

from workforce.utils import build_path_for_user_picture


class Calendar(models.Model):
    def __str__(self):
        return self.name

    calendar_id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=200, default="")


class Worker(models.Model):
    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if self.pk is None:
            self.calendar = Calendar.objects.create(name=self.name)
        super().save(**kwargs)

    name = models.CharField(max_length=200)
    timezone = models.CharField(max_length=200, default='America/Sao_Paulo')
    on_vacations = models.BooleanField(gettext_lazy('Disconsider worker when looking for free timeslots'), default=False)
    calendar = models.ForeignKey(Calendar, null=True, on_delete=models.SET_NULL)


class Availability(models.Model):
    def __str__(self):
        return f"{self.worker.name}: {self.get_day_of_the_week_display()} {self.start_time} - {self.end_time}"

    day_of_the_week = models.IntegerField(choices=enumerate(arrow.locales.EnglishLocale.day_names))
    start_time = models.TimeField()
    end_time = models.TimeField()
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)


class User(models.Model):
    def __str__(self):
        return f"{self.full_name} ({self.email_address})"

    email_address = models.EmailField()
    full_name = models.CharField(max_length=200)
    timezone = models.CharField(max_length=200, default='America/Sao_Paulo')
    photo = models.ImageField(upload_to=build_path_for_user_picture)


class WorkEvent(models.Model):
    def __str__(self):
        return f"{self.name}: {self.start} - {self.end}"

    event_id = models.IntegerField(unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    start = models.DateTimeField()
    end = models.DateTimeField()
