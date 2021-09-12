from django import forms
from django.utils.translation import gettext as _
from django.conf import settings
from babel.dates import format_datetime

from workforce.models import User


def free_timeslots_to_choices(timeslots, user_timezone):
    def timeslot_to_identifier(timeslot):
        return timeslot[0].isoformat()

    return [
        (
            timeslot_to_identifier(timeslot['timeslot']),
            format_datetime(
                timeslot['timeslot'][0].to(user_timezone).datetime,
                "EEEE, H'h'mm",
                locale=settings.LANGUAGE_CODE.split('-')[0]
            ).capitalize()
        )
        for timeslot in timeslots
    ]


class Registration(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email_address', 'timezone', 'photo']


class ScheduleAnAppointment(forms.Form):
    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['timeslots_available'] = forms.ChoiceField(
            label=_('Próximos horários disponíveis'),
            error_messages={
                'invalid_choice': _(
                    'Ops, alguém acabou de escolher este horário... '
                    'Por favor, escolha novamente.'
                )
            },
            choices=choices
        )

    comment = forms.CharField(
        label=_('Caso deseje tratar algo em especial, escreva abaixo'),
        required=False
    )
