from django.test import Client, RequestFactory, TestCase
from .models import OwnTrackLog
from accounts.models import BlogUser
import json


# Create your tests here.

class OwnTrackLogTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_own_track_log(self):
        user = BlogUser.objects.create_superuser(email="liangliangyy1@gmail.com",
                                                 username="liangliangyy1", password="liangliangyy1")

        self.client.login(username='liangliangyy1', password='liangliangyy1')
        s = OwnTrackLog()
        s.tid = 12
        s.lon = 123.234
        s.lat = 34.234
        s.save()
        rsp = self.client.get('/owntracks/show_maps')
        self.assertEqual(rsp.status_code, 200)
        rsp = self.client.get('/owntracks/get_datas')
        self.assertEqual(rsp.status_code, 200)
