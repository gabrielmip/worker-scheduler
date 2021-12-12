from django import forms
from django.utils.translation import gettext as _
from django.conf import settings
from babel.dates import format_datetime

from workforce.models import Patient


class Registration(forms.ModelForm):
    class Meta:
        model = Patient
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
        label=_('O que deseja tratar?'),
        help_text=_('Ex.: emocional, alguma dor física, ansiedade'),
        required=True
    )
