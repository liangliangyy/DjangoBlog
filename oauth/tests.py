from django.test import Client, RequestFactory, TestCase

from oauth.models import OAuthConfig


# Create your tests here.
class OAuthConfigTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_oauth_login_test(self):
        c = OAuthConfig()
        c.type = 'weibo'
        c.appkey = 'appkey'
        c.appsecret = 'appsecret'
        c.save()

        response = self.client.get('/oauth/oauthlogin?type=weibo')
        self.assertEqual(response.status_code, 302)
        self.assertTrue("api.weibo.com" in response.url)

        response = self.client.get('/oauth/authorize?type=weibo&code=code')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
