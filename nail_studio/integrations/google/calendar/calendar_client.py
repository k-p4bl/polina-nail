import datetime
import os
from pprint import pprint

from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleCalendar:
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            filename='nail-421623-69d9cb7e3d74.json', scopes=self.SCOPES
        )
        self.service = build('calendar', 'v3', credentials=credentials)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {'id': calendar_id}
        return self.service.calendarList().insert(
            body=calendar_list_entry
        ).execute()

    def add_event(self, date, time, service='Тест', description='Тест', hour=0, minute=30):
        time_end = datetime.time(hour=time.hour + hour, minute=time.minute + minute)

        event = {
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
        }

        self.service.events().insert(calendarId='d.pauline.w@gmail.com', body=event).execute()


if __name__ == '__main__':
    c = GoogleCalendar()
    pprint(c.add_calendar('d.pauline.w@gmail.com'))
