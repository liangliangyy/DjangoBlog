import json
from unittest.mock import patch

from django.conf import settings
from django.contrib import auth
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from djangoblog.utils import get_sha256
from oauth.models import OAuthConfig
from oauth.oauthmanager import BaseOauthManager


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


class OauthLoginTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.factory = RequestFactory()
        self.apps = self.init_apps()

    def init_apps(self):
        applications = [p() for p in BaseOauthManager.__subclasses__()]
        for application in applications:
            c = OAuthConfig()
            c.type = application.ICON_NAME.lower()
            c.appkey = 'appkey'
            c.appsecret = 'appsecret'
            c.save()
        return applications

    def get_app_by_type(self, type):
        for app in self.apps:
            if app.ICON_NAME.lower() == type:
                return app

    @patch("oauth.oauthmanager.WBOauthManager.do_post")
    @patch("oauth.oauthmanager.WBOauthManager.do_get")
    def test_weibo_login(self, mock_do_get, mock_do_post):
        weibo_app = self.get_app_by_type('weibo')
        assert weibo_app
        url = weibo_app.get_authorization_url()
        mock_do_post.return_value = json.dumps({"access_token": "access_token",
                                                "uid": "uid"
                                                })
        mock_do_get.return_value = json.dumps({
            "avatar_large": "avatar_large",
            "screen_name": "screen_name",
            "id": "id",
            "email": "email",
        })
        userinfo = weibo_app.get_access_token_by_code('code')
        self.assertEqual(userinfo.token, 'access_token')
        self.assertEqual(userinfo.openid, 'id')

    @patch("oauth.oauthmanager.GoogleOauthManager.do_post")
    @patch("oauth.oauthmanager.GoogleOauthManager.do_get")
    def test_google_login(self, mock_do_get, mock_do_post):
        google_app = self.get_app_by_type('google')
        assert google_app
        url = google_app.get_authorization_url()
        mock_do_post.return_value = json.dumps({
            "access_token": "access_token",
            "id_token": "id_token",
        })
        mock_do_get.return_value = json.dumps({
            "picture": "picture",
            "name": "name",
            "sub": "sub",
            "email": "email",
        })
        token = google_app.get_access_token_by_code('code')
        userinfo = google_app.get_oauth_userinfo()
        self.assertEqual(userinfo.token, 'access_token')
        self.assertEqual(userinfo.openid, 'sub')

    @patch("oauth.oauthmanager.GitHubOauthManager.do_post")
    @patch("oauth.oauthmanager.GitHubOauthManager.do_get")
    def test_github_login(self, mock_do_get, mock_do_post):
        github_app = self.get_app_by_type('github')
        assert github_app
        url = github_app.get_authorization_url()
        self.assertTrue("github.com" in url)
        self.assertTrue("client_id" in url)
        mock_do_post.return_value = "access_token=gho_16C7e42F292c6912E7710c838347Ae178B4a&scope=repo%2Cgist&token_type=bearer"
        mock_do_get.return_value = json.dumps({
            "avatar_url": "avatar_url",
            "name": "name",
            "id": "id",
            "email": "email",
        })
        token = github_app.get_access_token_by_code('code')
        userinfo = github_app.get_oauth_userinfo()
        self.assertEqual(userinfo.token, 'gho_16C7e42F292c6912E7710c838347Ae178B4a')
        self.assertEqual(userinfo.openid, 'id')

    @patch("oauth.oauthmanager.FaceBookOauthManager.do_post")
    @patch("oauth.oauthmanager.FaceBookOauthManager.do_get")
    def test_facebook_login(self, mock_do_get, mock_do_post):
        facebook_app = self.get_app_by_type('facebook')
        assert facebook_app
        url = facebook_app.get_authorization_url()
        self.assertTrue("facebook.com" in url)
        mock_do_post.return_value = json.dumps({
            "access_token": "access_token",
        })
        mock_do_get.return_value = json.dumps({
            "name": "name",
            "id": "id",
            "email": "email",
            "picture": {
                "data": {
                    "url": "url"
                }
            }
        })
        token = facebook_app.get_access_token_by_code('code')
        userinfo = facebook_app.get_oauth_userinfo()
        self.assertEqual(userinfo.token, 'access_token')

    @patch("oauth.oauthmanager.QQOauthManager.do_get", side_effect=[
        'access_token=access_token&expires_in=3600',
        'callback({"client_id":"appid","openid":"openid"} );',
        json.dumps({
            "nickname": "nickname",
            "email": "email",
            "figureurl": "figureurl",
            "openid": "openid",
        })
    ])
    def test_qq_login(self, mock_do_get):
        qq_app = self.get_app_by_type('qq')
        assert qq_app
        url = qq_app.get_authorization_url()
        self.assertTrue("qq.com" in url)
        token = qq_app.get_access_token_by_code('code')
        userinfo = qq_app.get_oauth_userinfo()
        self.assertEqual(userinfo.token, 'access_token')

    @patch("oauth.oauthmanager.WBOauthManager.do_post")
    @patch("oauth.oauthmanager.WBOauthManager.do_get")
    def test_weibo_authoriz_login_with_email(self, mock_do_get, mock_do_post):

        mock_do_post.return_value = json.dumps({"access_token": "access_token",
                                                "uid": "uid"
                                                })
        mock_user_info = {
            "avatar_large": "avatar_large",
            "screen_name": "screen_name1",
            "id": "id",
            "email": "email",
        }
        mock_do_get.return_value = json.dumps(mock_user_info)

        response = self.client.get('/oauth/oauthlogin?type=weibo')
        self.assertEqual(response.status_code, 302)
        self.assertTrue("api.weibo.com" in response.url)

        response = self.client.get('/oauth/authorize?type=weibo&code=code')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        user = auth.get_user(self.client)
        assert user.is_authenticated
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, mock_user_info['screen_name'])
        self.assertEqual(user.email, mock_user_info['email'])
        self.client.logout()

        response = self.client.get('/oauth/authorize?type=weibo&code=code')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        user = auth.get_user(self.client)
        assert user.is_authenticated
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, mock_user_info['screen_name'])
        self.assertEqual(user.email, mock_user_info['email'])

    @patch("oauth.oauthmanager.WBOauthManager.do_post")
    @patch("oauth.oauthmanager.WBOauthManager.do_get")
    def test_weibo_authoriz_login_without_email(self, mock_do_get, mock_do_post):

        mock_do_post.return_value = json.dumps({"access_token": "access_token",
                                                "uid": "uid"
                                                })
        mock_user_info = {
            "avatar_large": "avatar_large",
            "screen_name": "screen_name1",
            "id": "id",
        }
        mock_do_get.return_value = json.dumps(mock_user_info)

        response = self.client.get('/oauth/oauthlogin?type=weibo')
        self.assertEqual(response.status_code, 302)
        self.assertTrue("api.weibo.com" in response.url)

        response = self.client.get('/oauth/authorize?type=weibo&code=code')

        self.assertEqual(response.status_code, 302)

        oauth_user_id = int(response.url.split('/')[-1].split('.')[0])
        self.assertEqual(response.url, f'/oauth/requireemail/{oauth_user_id}.html')

        response = self.client.post(response.url, {'email': 'test@gmail.com', 'oauthid': oauth_user_id})

        self.assertEqual(response.status_code, 302)
        sign = get_sha256(settings.SECRET_KEY +
                          str(oauth_user_id) + settings.SECRET_KEY)

        url = reverse('oauth:bindsuccess', kwargs={
            'oauthid': oauth_user_id,
        })
        self.assertEqual(response.url, f'{url}?type=email')

        path = reverse('oauth:email_confirm', kwargs={
            'id': oauth_user_id,
            'sign': sign
        })
        response = self.client.get(path)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/oauth/bindsuccess/{oauth_user_id}.html?type=success')
        user = auth.get_user(self.client)
        from oauth.models import OAuthUser
        oauth_user = OAuthUser.objects.get(author=user)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, mock_user_info['screen_name'])
        self.assertEqual(user.email, 'test@gmail.com')
        self.assertEqual(oauth_user.pk, oauth_user_id)
