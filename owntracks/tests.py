from django.test import Client, RequestFactory, TestCase
from .models import OwnTrackLog
from accounts.models import BlogUser
from owntracks.views import convert_to_amap
import json


# Create your tests here.

class OwnTrackLogTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_own_track_log(self):
        o = {
            'tid': 12,
            'lat': 123.123,
            'lon': 134.341
        }

        self.client.post(
            '/owntracks/logtracks',
            json.dumps(o),
            content_type='application/json')
        length = len(OwnTrackLog.objects.all())
        self.assertEqual(length, 1)

        o = {
            'tid': 12,
            'lat': 123.123
        }

        self.client.post(
            '/owntracks/logtracks',
            json.dumps(o),
            content_type='application/json')
        length = len(OwnTrackLog.objects.all())
        self.assertEqual(length, 1)

        rsp = self.client.get('/owntracks/show_maps')
        self.assertEqual(rsp.status_code, 302)

        user = BlogUser.objects.create_superuser(
            email="liangliangyy1@gmail.com",
            username="liangliangyy1",
            password="liangliangyy1")

        self.client.login(username='liangliangyy1', password='liangliangyy1')
        s = OwnTrackLog()
        s.tid = 12
        s.lon = 123.234
        s.lat = 34.234
        s.save()
        convert_to_amap([s])
        rsp = self.client.get('/owntracks/show_dates')
        self.assertEqual(rsp.status_code, 200)
        rsp = self.client.get('/owntracks/show_maps')
        self.assertEqual(rsp.status_code, 200)
        rsp = self.client.get('/owntracks/get_datas')
        self.assertEqual(rsp.status_code, 200)
        rsp = self.client.get('/owntracks/get_datas?date=2018-02-26')
        self.assertEqual(rsp.status_code, 200)
