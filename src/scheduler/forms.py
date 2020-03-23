from django import forms
from django.utils.translation import gettext as _

from scheduler.services.calendar_service import get_one_free_timeslot_by_hour


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
        print(dropdown_choices)

        self.fields['timeslots_available'] = forms.ChoiceField(
            label=_('Next available timeslots'),
            choices=dropdown_choices
        )

    full_name = forms.CharField(label=_('Your full name'), max_length=200)
    email_address = forms.EmailField(
        label=_('Email address'),
        help_text=_('We will send an email with a reminder 15 minutes before the Reiki starts.')
    )

