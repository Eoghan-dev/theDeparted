from django.test import TestCase

# pages/tests.py
from django.http import HttpRequest
from django.test import SimpleTestCase
from django.urls import reverse

from . import views


class AppPageTests(SimpleTestCase):

    def test_index_page_status_code(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_journey_page_status_code(self):
        response = self.client.get('/journey')
        self.assertEquals(response.status_code, 200)

    def test_index_view_url_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)

    def test_journey_view_url_by_name(self):
        response = self.client.get(reverse('journey'))
        self.assertEquals(response.status_code, 200)

    def test_index_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dublinBus/index.html')


# Create your tests here.
