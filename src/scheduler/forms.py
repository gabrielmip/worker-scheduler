import arrow
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils.formats import date_format

from scheduler.services.calendar_service import get_one_free_timeslot_by_hour
from scheduler.services.events_service import can_user_schedule_event, get_user_next_event
from scheduler.services.user_service import get_user_by_email_address


def validate_no_future_event_associated(value):
    if not can_user_schedule_event(value):
        next_event = get_user_next_event(value)
        worker = next_event.calendar.worker_set.get()
        base_message = _('Ops, parece que você já tem uma sessão reservada. Ela está marcada para')
        start_time_as_string = (arrow.get(next_event.start)
            .to(next_event.user.timezone)
            .format('DD/MM, HH[h]mm'))

        raise ValidationError(
            _(f'{base_message} {start_time_as_string}.'),
            params={'value': value}
        )


def free_timeslots_to_choices(timeslots, user_timezone):
    def timeslot_to_identifier(calendar_id, timeslot):
        return f"{calendar_id}|{timeslot[0].isoformat()}|{timeslot[1].isoformat()}"

    return [
        (
            timeslot_to_identifier(**timeslot),
            date_format(
                timeslot['timeslot'][0].to(user_timezone).datetime,
                format='l, P',
                use_l10n=True
            )
        )
        for timeslot in timeslots
    ]


def build_free_timeslots_field(user_timezone):
    free_timeslots = get_one_free_timeslot_by_hour()
    dropdown_choices = free_timeslots_to_choices(free_timeslots, user_timezone)

    return forms.ChoiceField(
        label=_('Próximos horários disponíveis'),
        error_messages={
            'invalid_choice': _('Ops, alguém acabou de escolher este horário... Por favor, escolha novamente.')
        },
        choices=dropdown_choices
    )


class UserLogin(forms.Form):
    email_address = forms.EmailField(
        label=_('Endereço de email'),
        validators=[validators.EmailValidator, validate_no_future_event_associated]
    )


class ScheduleAnAppointment(forms.Form):
    def __init__(self, user_timezone, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timeslots_available'] = build_free_timeslots_field(user_timezone)


    comment = forms.CharField(label=_('Caso deseje tratar algo em especial, escreva abaixo'), required=False)


class UserInformation(forms.Form):
    full_name = forms.CharField(label=_('Seu nome completo'), max_length=200)
    photo = forms.ImageField(label=_('Sua foto'))


class UploadPhoto(forms.Form):
    photo = forms.ImageField(label=_('Sua foto'))
