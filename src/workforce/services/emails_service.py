import arrow

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from background_task import background

from workforce.models import WorkEvent


def setup_email_sending(work_event):
    ''' schedules email confirmation for now and a
        reminder 20 minutes prior to the work event start.
    '''
    when_to_remind = arrow.get(work_event.start).shift(minutes=-20).datetime

    send_confirmation_email(work_event.event_id)
    schedule_work_event_reminder(work_event.event_id, schedule=when_to_remind)


@background()
def send_confirmation_email(work_event_id):
    return send_event_email(
        work_event_id, 'confirmation_email', _('Confirmação de reserva de Reiki da distância'))


@background()
def schedule_work_event_reminder(work_event_id):
    send_event_email(work_event_id, 'reminder_email', _('Lembrete de sessão de Reiki da distância'))


def send_event_email(work_event_id, email_template_name, email_subject):
    ''' work_event_id instead of just using work_event directly because this
        function needs to receive only serializable arguments to make it
        possible to store it in a database.
    '''
    work_event = WorkEvent.objects.get(pk=work_event_id)
    cancelling_url = f"{settings.EXTERNAL_URL_BASE_PATH}/cancel/{work_event.event_id}"
    localized_event_start = arrow.get(work_event.start).to(work_event.user.timezone).datetime
    context = {
        'event': work_event,
        'localized_event_start': localized_event_start,
        'cancelling_url': cancelling_url
    }
    message = render_to_string(f'emails/{email_template_name}.txt', context)

    return send_mail(
        email_subject,
        message,
        settings.EMAIL_HOST_USER,
        [work_event.user.email_address]
    )
