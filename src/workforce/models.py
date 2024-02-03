from enum import Enum
import pytz
import arrow

from django.contrib.auth.models import AbstractUser
from django.db.models.query_utils import Q
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from workforce.utils import build_path_for_user_picture, enum_entries


TIMEZONES_AS_CHOICES = [
    (a, a.replace("_", " ")) for a in pytz.common_timezones
]


class MyUser(AbstractUser):
    first_login = models.BooleanField(_("Primeiro login?"), default=False)

    class Meta:
        db_table = "auth_user"
        verbose_name = _("Usuário")
        verbose_name_plural = _("Usuários")


class Calendar(models.Model):
    def __str__(self):
        return str(self.calendar_id)

    calendar_id = models.IntegerField(unique=True, primary_key=True)

    class Meta:
        verbose_name = _("Calendário")
        verbose_name_plural = _("Calendários")


class WorkerQuerySet(models.QuerySet):
    def active_workers(self):
        return self.filter(on_vacations=False)


class Worker(models.Model):
    def __str__(self):
        return str(self.auth_user)

    def save(self, **kwargs):
        if self.pk is None:
            Calendar.objects.create()
            self.calendar = Calendar.objects.latest("calendar_id")
        super().save(**kwargs)

    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    timezone = models.CharField(
        _("Fuso horário"),
        max_length=200,
        choices=TIMEZONES_AS_CHOICES,
        default="America/Sao_Paulo",
    )
    on_vacations = models.BooleanField(
        _("Considerar que esta pessoa está de folga"), default=False
    )
    calendar = models.ForeignKey(
        Calendar, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("Trabalhadora")
        verbose_name_plural = _("Trabalhadoras")

    objects = WorkerQuerySet.as_manager()


class Availability(models.Model):
    def __str__(self):
        return f"{str(self.worker.auth_user)}: {self.get_day_of_the_week_display()} {self.start_time} - {self.end_time}"

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    day_of_the_week = models.IntegerField(
        _("Dia da semana"),
        choices=enumerate(arrow.locales.BrazilianPortugueseLocale.day_names),
    )
    start_time = models.TimeField(_("Hora de início"))
    end_time = models.TimeField(_("Hora de término"))
    is_live = models.BooleanField(_("Presencial"), default=False)

    class Meta:
        verbose_name = _("Disponibilidade")
        verbose_name_plural = _("Disponibilidades")


class Patient(models.Model):
    def __str__(self):
        return f"{self.full_name} ({self.email_address})"

    def save(self, **kwargs):
        if self.auth_user is None:
            self.auth_user = MyUser.objects.create_user(
                username=self.email_address,
                email=self.email_address,
                first_name=self.full_name,
                first_login=True,
                password=MyUser.objects.make_random_password(length=30),
            )
        else:
            self.auth_user.username = self.email_address
            self.auth_user.email = self.email_address
            self.auth_user.first_name = self.full_name
        super().save(**kwargs)

    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE
    )
    full_name = models.CharField(
        verbose_name=_("Seu nome completo"), max_length=200
    )
    email_address = models.EmailField(
        verbose_name=_("Endereço de email"),
        unique=True,
        help_text=_(
            "Nós vamos te enviar um email com um lembrete antes do início da sessão."
        ),
    )
    timezone = models.CharField(
        verbose_name=_("Fuso horário"),
        max_length=200,
        choices=TIMEZONES_AS_CHOICES,
        default="America/Sao_Paulo",
    )
    photo = models.ImageField(
        verbose_name=_("Uma foto do seu rosto"),
        upload_to=build_path_for_user_picture,
    )
    can_schedule_live = models.BooleanField(
        verbose_name=_("Pode agendar presencial?"),
        default=True,
    )

    class Meta:
        verbose_name = _("Paciente")
        verbose_name_plural = _("Pacientes")


class WorkEventQuerySet(models.QuerySet):
    def active_work_events(self):
        return self.filter(canceled_at=None)


class WorkEvent(models.Model):
    def __str__(self):
        return f"{str(self.user)}: {self.start} - {self.end}"

    event_id = models.AutoField(unique=True, primary_key=True)
    user = models.ForeignKey(Patient, on_delete=models.CASCADE)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500, default="")
    start = models.DateTimeField()
    end = models.DateTimeField()
    is_live = models.BooleanField(_("Presencial"), default=False)
    cancelling_token = models.CharField(
        max_length=256, default=None, null=True
    )
    created_at = models.DateTimeField(
        _("Data criação"), auto_now=True, blank=True
    )
    canceled_at = models.DateTimeField(
        _("Data cancelamento"),
        null=True,
        default=None,
        blank=True,
    )

    objects = WorkEventQuerySet.as_manager()

    class Meta:
        verbose_name = _("Evento de trabalho")
        verbose_name_plural = _("Eventos de trabalho")
        constraints = [
            models.UniqueConstraint(
                fields=["start", "calendar_id", "user_id"],
                condition=Q(canceled_at=None),
                name="idx_active_event_start_calendar_user",
            )
        ]


# class NotificationType(Enum):

#     invalid_email = 'Email inválido'
#     no_face_on_photo = 'Foto não mostra o rosto'
#     other_person_on_photo = 'Foto e nome são de pessoas diferentes'


# class Notification(models.Model):

#     user_id = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True, # in case the notification is for every one
#         on_delete=models.CASCADE
#     )
#     notification_type = models.CharField( _('Notificação'), max_length=256, choices=enum_entries(NotificationType))
#     custom_message = models.CharField( _('Mensagem personalizada'), null=True, max_length=500)
#     active = models.BooleanField( _('Ativa'), default=True)
#     seen_count = models.IntegerField(_('Vezes vista'), default=0)
#     last_seen_at = models.DateTimeField(_('Última visualização'), null=True)
#     created_at = models.DateTimeField( _('Data de criação'), auto_now=True, blank=True)
