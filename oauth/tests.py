from django.test import TestCase

# Create your tests here.

class OAuthTet(TestCase):
    def setUp(self):
        pass


from oauth.oauthmanager import WBOauthManager
from django.conf import settings
settings.OAHUTH['sina']
manager=WBOauthManager(client_id=settings.OAHUTH['sina']['appkey'],client_secret=settings.OAHUTH['sina']['appsecret'],callback_url=settings.OAHUTH['sina']['callbackurl'])