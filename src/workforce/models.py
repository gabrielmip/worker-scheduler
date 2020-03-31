import arrow
from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.utils.translation import gettext_lazy as _

from workforce.utils import build_path_for_user_picture


class Calendar(models.Model):
    def __str__(self):
        return str(self.calendar_id)

    calendar_id = models.IntegerField(unique=True, primary_key=True)

    class Meta:
        verbose_name = _('Calendário')
        verbose_name_plural = _('Calendários')


class Worker(models.Model):
    def __str__(self):
        return str(self.auth_user)

    def save(self, **kwargs):
        if self.pk is None:
            Calendar.objects.create()
            self.calendar = Calendar.objects.latest('calendar_id')
        super().save(**kwargs)

    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    timezone = models.CharField(_('Fuso horário'), max_length=200, default='America/Sao_Paulo')
    on_vacations = models.BooleanField(_('Considerar que esta pessoa está de folga'), default=False)
    calendar = models.ForeignKey(Calendar, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('Pessoa trabalhadora')
        verbose_name_plural = _('Pessoas trabalhadoras')


class Availability(models.Model):
    def __str__(self):
        return f"{str(self.worker.auth_user)}: {self.get_day_of_the_week_display()} {self.start_time} - {self.end_time}"

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    day_of_the_week = models.IntegerField(_('Dia da semana'), choices=enumerate(arrow.locales.BrazilianPortugueseLocale.day_names))
    start_time = models.TimeField(_('Hora de início'))
    end_time = models.TimeField(_('Hora de término'))

    class Meta:
        verbose_name = _('Disponibilidade')
        verbose_name_plural = _('Disponibilidades')


class User(models.Model):
    def __str__(self):
        return f"{self.full_name} ({self.email_address})"

    email_address = models.EmailField()
    full_name = models.CharField(max_length=200)
    timezone = models.CharField(max_length=200, default='America/Sao_Paulo')
    photo = models.ImageField(upload_to=build_path_for_user_picture)

    class Meta:
        verbose_name = _('Paciente')
        verbose_name_plural = _('Pacientes')


class WorkEvent(models.Model):
    def __str__(self):
        return f"{str(self.user)}: {self.start} - {self.end}"

    event_id = models.IntegerField(unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500, default='')
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        verbose_name = _('Evento de trabalho')
        verbose_name_plural = _('Eventos de trabalho')
