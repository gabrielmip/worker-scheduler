from django import forms
from django.utils.translation import gettext as _


class ScheduleAnAppointment(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timeslots_available'] = forms.ChoiceField(
            label=_('Next available timeslots'),
            choices=[('19:00', 'Quinta 19:00')]
        )

    full_name = forms.CharField(label=_('Your full name'), max_length=200)
    email_address = forms.EmailField(
        label=_('Email address'),
        help_text=_('We will send an email with a reminder 15 minutes before the Reiki starts.')
    )

