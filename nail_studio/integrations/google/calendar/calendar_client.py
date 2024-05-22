import datetime
import os
from pprint import pprint

from django.core.exceptions import BadRequest
from dotenv import load_dotenv, find_dotenv

from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleCalendarEvent:
    def __init__(self, service, event_id: str):
        self.calendar_id = 'd.pauline.w@gmail.com'
        self.service = service
        self.event_id = event_id
        self.event = self.service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()

    def change(self,
               date: datetime.date | None,
               time: datetime.time | None,
               service: str | None,
               description: str | None,
               hour: int | None,
               minute: int | None):
        initial_end_date, initial_end_time = self.event['end']['dateTime'].split('T')
        initial_start_date, initial_start_time = self.event['start']['dateTime'].split('T')
        # Если изменилась услуга
        if service is not None and hour is not None and minute is not None:
            self.event['summary'] = '(Маникюр)' + service

            # дата(НЕ изменилась) время(НЕ изменилось), меняется время(конца)
            if time is None and date is None:
                time = datetime.time(int(initial_start_time[:2]))
                time_end = datetime.time(hour=time.hour + hour, minute=time.minute + minute).strftime('%H:%M')
                self.event['end']['dateTime'] = initial_end_date + 'T' + time_end + initial_end_time[5:]
        else:
            hour = int(initial_end_time[:2]) - int(initial_start_time[:2])
            minute = int(initial_end_time[3:5]) - int(initial_start_time[3:5])

        # время ИЗМЕНИЛОСЬ, меняется время(конца и начала)
        if time is not None:
            # дата НЕ изменилась
            # или дата ИЗМЕНИЛАСЬ, меняется дата(конца и начала)
            date = initial_start_date if date is None else date.strftime('%Y-%m-%d')
            self.event['start']['dateTime'] = (date + 'T' + time.strftime('%H:%M') +
                                               initial_start_time[5:])

            time_end = datetime.time(hour=time.hour + hour, minute=time.minute + minute).strftime('%H:%M')
            self.event['end']['dateTime'] = date + 'T' + time_end + initial_end_time[5:]

        # дата ИЗМЕНИЛАСЬ время НЕ изменилось, меняется дата(конца и начала)
        elif date is not None:
            self.event['start']['dateTime'] = date.strftime('%Y-%m-%d') + 'T' + initial_start_time

            time = datetime.time(int(initial_start_time[:2]))
            time_end = datetime.time(hour=time.hour + hour, minute=time.minute + minute).strftime('%H:%M')
            self.event['end']['dateTime'] = date.strftime('%Y-%m-%d') + 'T' + time_end + initial_end_time[5:]

        if description is not None:
            self.event['description'] = description

        self.service.events().update(calendarId=self.calendar_id, eventId=self.event_id, body=self.event).execute()

    def delete(self):
        self.service.events().delete(calendarId=self.calendar_id, eventId=self.event_id).execute()


class GoogleCalendar:
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    # For develop ____________________________________________
    load_dotenv(find_dotenv())
    # ________________________________________________________

    info = {
        "type": "service_account",
        "project_id": "nail-421623",
        "private_key_id": os.getenv('GOOGLE_CALENDAR_PRIVATE_KEY_ID'),
        "private_key": os.getenv('GOOGLE_CALENDAR_PRIVATE_KEY').replace('\\n', '\n'),
        "client_email": "polina@nail-421623.iam.gserviceaccount.com",
        "client_id": "103713274168080944607",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/polina%40nail-421623.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_info(
            info=self.info, scopes=self.SCOPES
        )
        self.service = build('calendar', 'v3', credentials=credentials)
        self.calendar_id = 'd.pauline.w@gmail.com'

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {'id': calendar_id}
        return self.service.calendarList().insert(
            body=calendar_list_entry
        ).execute()

    def _get_event_id(self, description: str, start_date: datetime.date, start_time: datetime.time) -> str:
        date_time = start_date.strftime('%Y-%m-%d') + 'T' + start_time.strftime('%H:%M:%S') + '+08:00'

        events_list = self.service.events().list(calendarId=self.calendar_id, q=description).execute()['items']
        if events_list:
            for event in events_list:
                if event['start']['dateTime'] == date_time:
                    return event['id']

        raise BadRequest(f'Не существует события в календаре с описанием "{description}", датой "{start_date}"'
                         f' и временем "{start_time}"')

    def get_event(self,
                  description: str,
                  start_date: datetime.date,
                  start_time: datetime.time) -> GoogleCalendarEvent:
        event_id = self._get_event_id(description, start_date, start_time)
        return GoogleCalendarEvent(self.service, event_id)

    def add_event(self, date, time, service='Тест', description='Тест', hour=0, minute=30):
        time_end = datetime.time(hour=time.hour + hour, minute=time.minute + minute)

        minutes_for_reminders = (24 - (20 - int(time.strftime('%H')))) * 60

        body = {
            'summary': '(Маникюр)' + service,
            'description': description,
            'start': {
                'dateTime': date + 'T' + time.strftime('%H:%M:%S'),
                'timeZone': 'Asia/Irkutsk',
            },
            'end': {
                'dateTime': date + 'T' + time_end.strftime('%H:%M:%S'),
                'timeZone': 'Asia/Irkutsk',
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {
                        "method": 'popup',
                        "minutes": minutes_for_reminders
                    },
                    {
                        "method": 'email',
                        "minutes": minutes_for_reminders
                    }
                ]
            },
        }

        self.service.events().insert(calendarId=self.calendar_id, body=body).execute()


if __name__ == '__main__':
    c = GoogleCalendar()
    pprint(c.add_calendar('d.pauline.w@gmail.com'))
