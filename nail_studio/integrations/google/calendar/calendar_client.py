import datetime
import os
from pprint import pprint
from dotenv import load_dotenv, find_dotenv

from google.oauth2 import service_account
from googleapiclient.discovery import build


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

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {'id': calendar_id}
        return self.service.calendarList().insert(
            body=calendar_list_entry
        ).execute()

    def add_event(self, date, time, service='Тест', description='Тест', hour=0, minute=30):
        time_end = datetime.time(hour=time.hour + hour, minute=time.minute + minute)

        minutes_for_reminders = (24 - (20 - int(time.strftime('%H')))) * 60

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
            # 'attendees': [
            #     {'email': 'd.pauline.w@gmail.com'},
            # ],
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

        self.service.events().insert(calendarId='d.pauline.w@gmail.com', body=event).execute()


if __name__ == '__main__':
    c = GoogleCalendar()
    pprint(c.add_calendar('d.pauline.w@gmail.com'))
