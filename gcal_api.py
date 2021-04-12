from googleapiclient import sample_tools
from datetime import datetime, timedelta
from config import DATE_FORMAT, GCAL_DATE_FORMAT, default_args, SCOPES
from pytz import timezone

def event_start(event):
    if 'date' in event['start'].keys():
        return event['start']['date']
    else:
        return event['start']['dateTime']


def _create_service():
    return sample_tools.init('', 'calendar', 'v3', __doc__, __file__, scope=SCOPES)


class GoogleCalendarManager:
    def __init__(self):
        self._service, self._flags = _create_service()
        self._calendars = self._get_calendars()['items']

    def _get_calendar_id(self, calendar_name):
        for cal in self._calendars:
            if cal['summary'] == calendar_name:
                return cal['id']
        else:
            return None

    def _get_calendars(self):
        return self._service.calendarList().list().execute()

    def get_events(self, calendar_name, order_by=None, time_min=None, time_max=None, max_results=None):
        if time_max is not None:
            time_max = (datetime.strptime(time_max, DATE_FORMAT) + timedelta(days=1)).strftime(GCAL_DATE_FORMAT)
        if time_min is not None:
            time_min = datetime.strptime(time_min, DATE_FORMAT).strftime(GCAL_DATE_FORMAT)
        event_list = self._service.events().list(calendarId=self._get_calendar_id(calendar_name), orderBy=order_by, timeMin=time_min, timeMax=time_max, maxResults=max_results).execute()['items']
        return sorted(event_list, key=lambda e: event_start(e))

    def get_calendars(self, sort_by_summary=True):
        if sort_by_summary:
            return sorted(self._calendars, key=lambda c: c['summary'])
        else:
            return self._calendars

    def insert_event(self, calendar_name, title, start_time, duration=default_args['new_event_duration'], attendees=None):
        calendar_id = self._get_calendar_id(calendar_name)
        body_start_time = timezone(default_args['time_zone']).localize(datetime.strptime(start_time,"%Y-%m-%d %H:%M"))
        body_end_time = body_start_time + timedelta(minutes=duration)

        body = {
            'summary': title,
            'start': {'dateTime': body_start_time.isoformat(), 'timZone': default_args['time_zone']},
            'end': {'dateTime': body_end_time.isoformat()},
            'attendees': [{'email': attendee } for attendee in attendees.split(',')]
        }
        print(body)
        self._service.events().insert(calendarId=calendar_id, body=body).execute()


if __name__ == "__main__":
    pass
