import arrow
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from scheduler.services.calendar_service import get_one_free_timeslot_by_hour
from scheduler.repositories.event_repository import can_user_schedule_event, get_user_next_event


def validate_email_has_no_future_event_associated(value):
    if not can_user_schedule_event(value):
        next_event = get_user_next_event(value)
        worker = next_event.calendar.worker_set.get()
        base_message = _('Oops, it looks like you already have a reservation. It is scheduled for')
        start_time_as_string = (arrow.get(next_event.start)
            .to(worker.timezone)
            .format('DD/MM, HH[h]mm'))

        raise ValidationError(
            _(f'{base_message} {start_time_as_string}.'),
            params={'value': value}
        )


def free_timeslots_to_choices(timeslots):
    def timeslot_to_identifier(calendar_id, timeslot):
        return f"{calendar_id}|{timeslot[0].isoformat()}|{timeslot[1].isoformat()}"

    return [
        (
            timeslot_to_identifier(**timeslot),
            timeslot['timeslot'][0].format('dddd, HH:mm')
        )
        for timeslot in timeslots
    ]


class ScheduleAnAppointment(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        free_timeslots = get_one_free_timeslot_by_hour()
        dropdown_choices = free_timeslots_to_choices(free_timeslots)

        self.fields['timeslots_available'] = forms.ChoiceField(
            label=_('Next available timeslots'),
            choices=dropdown_choices
        )

    full_name = forms.CharField(label=_('Your full name'), max_length=200)
    email_address = forms.EmailField(
        label=_('Email address'),
        help_text=_('We will send an email with a reminder 15 minutes before the Reiki starts.'),
        validators=[validators.EmailValidator, validate_email_has_no_future_event_associated]
    )


class UploadPhoto(forms.Form):
    photo = forms.ImageField(label=_('Your picture'))
