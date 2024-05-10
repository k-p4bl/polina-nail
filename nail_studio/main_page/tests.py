import datetime
import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.test import Client

from main_page import models


# Create your tests here.
class SignUpView(TestCase):
    def setUp(self):
        pass

    def test_list_of_dates_with_three_time(self):
        now = timezone.localtime()
        d = models.Date.objects.create(date=datetime.date(now.year, now.month, now.day))
        for i in range(3):
            try:
                time = models.Time.objects.create(time=datetime.time(now.hour + i, ))
            except ValueError:
                time = models.Time.objects.create(time=datetime.time(now.hour + i - 12, ))
            time.date_set.add(d)
        client = Client()
        response = client.get(reverse('sign_up', ))
        self.assertEqual(response.context['dates'], [f'{now.strftime('%Y')}-{now.strftime('%m')}-{now.strftime('%d')}'])

    def test_validate_date_with_date_is_in_the_database(self):
        now = timezone.localtime()
        d = models.Date.objects.create(date=datetime.date(now.year, now.month, now.day))
        time = models.Time.objects.create(time=datetime.time(13, ))
        time.date_set.add(d)
        c = Client()
        json_response = c.post(reverse('validate_date', ),
                               [f'{now.year}-{now.month}-{now.day}'],
                               content_type='application/json')
        response = json.loads(json_response.content)
        self.assertEqual(response, {'10': False, '13': True, '16': False})

    def test_validate_date_with_date_is_not_in_the_database(self):
        now = timezone.localtime()
        c = Client()
        json_response = c.post(reverse('validate_date', ),
                               [f'{now.year}-{now.month}-{now.day}'],
                               content_type='application/json')
        response = json.loads(json_response.content)
        self.assertEqual(response, {'10': False, '13': False, '16': False})

    def test_validate_date_without_date(self):
        c = Client()
        json_response = c.post(reverse('validate_date', ), [], content_type='application/json')
        response = json.loads(json_response.content)
        self.assertEqual(response, {'10': True, '13': True, '16': True})


class SignUpFinishView(TestCase):

    def setUp(self):
        self.service = 'Маникюр'
        self.last_name = 'Куборский'
        self.first_name = 'Павел'
        self.patronymic = 'Александрович'
        self.phone_number = '+7 (904) 179-00-17'
        self.date = timezone.localdate().strftime('%Y-%m-%d')
        self.time = '13'

    def test_if_service_is_default(self):
        c = Client()
        response = c.post(reverse('sign_up_finish', ), {'service': 'default',
                                                        'person-name': self.last_name + self.first_name + self.patronymic,
                                                        'phone-number': self.phone_number,
                                                        'date': self.date,
                                                        'time': self.time}, follow=True)

        self.assertEqual(response.context['service_is_default'], 'True')
        self.assertEqual(response.redirect_chain[0][1], 301)
        self.assertContains(response, 'Услуга не выбрана')

    def test_if_service_is_not_default(self):
        c = Client()
        response = c.post(reverse('sign_up_finish', ), {'service': self.service,
                                                        'person-name': self.last_name + self.first_name + self.patronymic,
                                                        'phone-number': self.phone_number,
                                                        'date': self.date,
                                                        'time': self.time})

        self.assertEqual(response.status_code, 200)

    def test_if_date_is_already_taken(self):
        date = models.Date.objects.create(date=timezone.localdate())
        time = models.Time.objects.create(time=datetime.time(13, ))
        time.date_set.add(date)
        c = Client()
        response = c.post(reverse('sign_up_finish', ), {'service':  self.service,
                                                        'person-name': self.last_name + self.first_name + self.patronymic,
                                                        'phone-number': self.phone_number,
                                                        'date': self.date,
                                                        'time': self.time}, follow=True)

        self.assertEqual(response.redirect_chain[0][1], 301)
        self.assertContains(response, 'К сожалению выбранное время уже занято.')

    def test_person_name_uncorrected_format(self):
        c = Client()
        response = c.post(reverse('sign_up_finish', ), {'service': self.service,
                                                        'person-name': self.last_name + self.first_name,
                                                        'phone-number': self.phone_number,
                                                        'date': self.date,
                                                        'time': self.time}, follow=True)
        self.assertEqual(response.redirect_chain[0][1], 301)
        self.assertContains(response, 'Неверный формат имени')
        self.assertEqual(response.context['person_name_is_correct'], 'False')

    def test_person_name_correct_format(self):
        c = Client()
        response = c.post(reverse('sign_up_finish', ), {'service': self.service,
                                                        'person-name': self.last_name + self.first_name + self.patronymic,
                                                        'phone-number': self.phone_number,
                                                        'date': self.date,
                                                        'time': self.time})

        self.assertEqual(response.status_code, 200)

    def test_both_errors(self):
        c = Client()
        response = c.post(reverse('sign_up_finish', ), {'service': 'default',
                                                        'person-name': self.last_name + self.first_name,
                                                        'phone-number': self.phone_number,
                                                        'date': self.date,
                                                        'time': self.time}, follow=True)

        self.assertEqual(response.redirect_chain[0][1], 301)
        self.assertContains(response, 'Услуга не выбрана')
        self.assertContains(response, 'Неверный формат имени')
        self.assertEqual(response.context['service_is_default'], 'True')
        self.assertEqual(response.context['person_name_is_correct'], 'False')
