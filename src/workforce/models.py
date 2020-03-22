from django.db import models

import scheduler.repositories.google_agenda_repository as google_repo


class CalendarManager(models.Manager):
    def create_calendar(self, user_name, timezone):
        calendar_name = user_name
        new_google_calendar_id = google_repo.create_calendar(calendar_name, timezone)
        return self.create(name=calendar_name, calendar_id=new_google_calendar_id)


class Calendar(models.Model):
    def __str__(self):
        return self.name

    calendar_id = models.CharField(max_length=200, unique=True, primary_key=True)
    name = models.CharField(max_length=200, default="")
    objects = CalendarManager()


class Worker(models.Model):
    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if self.pk is None:
            self.calendar = Calendar.objects.create_calendar(self.name, self.timezone)
        super().save(**kwargs)

    name = models.CharField(max_length=200)
    timezone = models.CharField(max_length=200, default='America/Sao_Paulo')
    calendar = models.ForeignKey(Calendar, null=True, on_delete=models.SET_NULL)
