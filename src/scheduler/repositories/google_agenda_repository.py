import arrow

from scheduler.connectors.google_connector import GOOGLE_CONNECTOR


SCHEDULE_SUMMARY_PREFIX = '[RDC]'


def get_calendars():
    calendars = GOOGLE_CONNECTOR.calendarList().list().execute()

    return [
        {'id': calendar['id'], 'name': calendar['summary']}
        for calendar in calendars['items']
        if calendar['summary'].startswith(SCHEDULE_SUMMARY_PREFIX)
    ]


def create_calendar(name, timezone):
    body = {
        "kind": "calendar#calendar",
        "summary": f"{SCHEDULE_SUMMARY_PREFIX} {name}",
        "timeZone": timezone
    }
    created = GOOGLE_CONNECTOR.calendars().insert(body=body).execute()

    return created['id']


def _busy_item_to_dates(busy_item):
    return (arrow.get(busy_item['start']), arrow.get(busy_item['end']))


def get_freebusy_from_calendars(calendars, start, end, timezone):
    body = {
        "calendarExpansionMax": len(calendars),
        "groupExpansionMax": 0,
        "timeMax": end.isoformat(),
        "items": calendars,
        "timeMin": start.isoformat(),
        "timeZone": timezone
    }
    freebusy_response = GOOGLE_CONNECTOR.freebusy().query(body=body).execute()

    return {
        calendar_id: [_busy_item_to_dates(busy_item) for busy_item in calendar['busy']]
        for calendar_id, calendar in freebusy_response['calendars'].items()
    }


def create_event(name, description, calendar_id, start, end):
    body = {
        "summary": name,
        "description": description,
        "start": {
            "dateTime": start.isoformat()
        },
        "end": {
            "dateTime": end.isoformat()
        }
    }
    created = GOOGLE_CONNECTOR.events().insert(calendarId=calendar_id, body=body).execute()

    return created['id']


def edit_event_description(event_id, calendar_id, description):
    body = {
        "description": description
    }

    return GOOGLE_CONNECTOR.events().patch(calendarId=calendar_id, body=body, eventId=event_id).execute()

