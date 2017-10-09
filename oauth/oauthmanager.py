#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: oauthmanager.py
@time: 2016/11/26 下午5:09
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from oauth.models import OAuthUser
from django.conf import settings
import requests
import json
import urllib.parse
from DjangoBlog.utils import logger, parse_dict_to_url


class BaseOauthManager(metaclass=ABCMeta):
    """获取用户授权"""
    AUTH_URL = None
    """获取token"""
    TOKEN_URL = None
    """获取用户信息"""
    API_URL = None
    '''icon图标名'''
    ICON_NAME = None

    def __init__(self, access_token=None, openid=None):
        self.access_token = access_token
        self.openid = openid

    @property
    def is_access_token_set(self):
        return self.access_token is not None

    @property
    def is_authorized(self):
        return self.is_access_token_set and self.access_token is not None and self.openid is not None

    @abstractmethod
    def get_authorization_url(self, nexturl='/'):
        pass

    @abstractmethod
    def get_access_token_by_code(self, code):
        pass

    @abstractmethod
    def get_oauth_userinfo(self):
        pass

    def do_get(self, url, params):
        rsp = requests.get(url=url, params=params)
        return rsp.text

    def do_post(self, url, params):
        rsp = requests.post(url, params)
        return rsp.text


class WBOauthManager(BaseOauthManager):
    AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
    TOKEN_URL = 'https://api.weibo.com/oauth2/access_token'
    API_URL = 'https://api.weibo.com/2/users/show.json'
    ICON_NAME = 'weibo'

    def __init__(self, access_token=None, openid=None):
        self.client_id = settings.OAHUTH['sina']['appkey']
        self.client_secret = settings.OAHUTH['sina']['appsecret']
        self.callback_url = settings.OAHUTH['sina']['callbackurl']
        super(WBOauthManager, self).__init__(access_token=access_token, openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.callback_url + '&next_url=' + nexturl
        }
        url = self.AUTH_URL + "?" + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):

        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.callback_url
        }
        rsp = self.do_post(self.TOKEN_URL, params)
        print(rsp)
        try:
            obj = json.loads(rsp)
            self.access_token = str(obj['access_token'])
            self.openid = str(obj['uid'])
            return self.get_oauth_userinfo()
        except:
            return None

    def get_oauth_userinfo(self):
        if not self.is_authorized:
            return None
        params = {
            'uid': self.openid,
            'access_token': self.access_token
        }
        rsp = self.do_get(self.API_URL, params)
        try:

            datas = json.loads(rsp)
            user = OAuthUser()
            user.picture = datas['avatar_large']
            user.nikename = datas['screen_name']
            user.openid = datas['id']
            user.type = 'weibo'
            user.token = self.access_token
            if 'email' in datas and datas['email']:
                user.email = datas['email']
            return user
        except:
            logger.info('weibo oauth error.rsp:' + rsp)
            return None


class GoogleOauthManager(BaseOauthManager):
    AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
    API_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
    ICON_NAME = 'google'

    def __init__(self, access_token=None, openid=None):
        self.client_id = settings.OAHUTH['google']['appkey']
        self.client_secret = settings.OAHUTH['google']['appsecret']
        self.callback_url = settings.OAHUTH['google']['callbackurl']
        super(GoogleOauthManager, self).__init__(access_token=access_token, openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.callback_url,
            'scope': 'openid email',
        }
        # url = self.AUTH_URL + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        url = self.AUTH_URL + "?" + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,

            'redirect_uri': self.callback_url
        }
        rsp = self.do_post(self.TOKEN_URL, params)

        obj = json.loads(rsp)
        try:
            self.access_token = str(obj['access_token'])
            self.openid = str(obj['id_token'])
            logger.info(self.ICON_NAME + ' oauth ' + rsp)
            return self.access_token
        except:
            logger.info(self.ICON_NAME + ' oauth error ' + rsp)
            return None

    def get_oauth_userinfo(self):
        if not self.is_authorized:
            return None
        params = {
            'access_token': self.access_token
        }
        rsp = self.do_get(self.API_URL, params)
        try:

            datas = json.loads(rsp)
            user = OAuthUser()
            user.picture = datas['picture']
            user.nikename = datas['name']
            user.openid = datas['sub']
            user.token = self.access_token
            user.type = 'google'
            if datas['email']:
                user.email = datas['email']
            return user
        except:
            logger.info('google oauth error.rsp:' + rsp)
            return None


class GitHubOauthManager(BaseOauthManager):
    AUTH_URL = 'https://github.com/login/oauth/authorize'
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    API_URL = 'https://api.github.com/user'
    ICON_NAME = 'github'

    def __init__(self, access_token=None, openid=None):
        self.client_id = settings.OAHUTH['github']['appkey']
        self.client_secret = settings.OAHUTH['github']['appsecret']
        self.callback_url = settings.OAHUTH['github']['callbackurl']
        super(GitHubOauthManager, self).__init__(access_token=access_token, openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.callback_url + '&next_url=' + nexturl,
            'scope': 'user'
        }
        # url = self.AUTH_URL + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        url = self.AUTH_URL + "?" + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,

            'redirect_uri': self.callback_url
        }
        rsp = self.do_post(self.TOKEN_URL, params)

        try:
            from urllib import parse
            r = parse.parse_qs(rsp)
            self.access_token = (r['access_token'][0])
            return self.access_token
        except:
            return None

    def get_oauth_userinfo(self):

        params = {
            'access_token': self.access_token
        }
        rsp = self.do_get(self.API_URL, params)

        try:
            datas = json.loads(rsp)
            user = OAuthUser()
            user.picture = datas['avatar_url']
            user.nikename = datas['name']
            user.openid = datas['id']
            user.type = 'github'
            user.token = self.access_token
            if datas['email']:
                user.email = datas['email']

            return user
        except:
            logger.info('github oauth error.rsp:' + rsp)
            return None


class FaceBookOauthManager(BaseOauthManager):
    AUTH_URL = 'https://www.facebook.com/v2.10/dialog/oauth'
    TOKEN_URL = 'https://graph.facebook.com/v2.10/oauth/access_token'
    API_URL = 'https://graph.facebook.com/me'
    ICON_NAME = 'facebook'

    def __init__(self, access_token=None, openid=None):
        self.client_id = settings.OAHUTH['facebook']['appkey']
        self.client_secret = settings.OAHUTH['facebook']['appsecret']
        self.callback_url = settings.OAHUTH['facebook']['callbackurl']
        super(FaceBookOauthManager, self).__init__(access_token=access_token, openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.callback_url,  # + '&next_url=' + nexturl,
            'scope': 'email,public_profile'
        }
        url = self.AUTH_URL + "?" + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            # 'grant_type': 'authorization_code',
            'code': code,

            'redirect_uri': self.callback_url
        }
        rsp = self.do_post(self.TOKEN_URL, params)

        try:
            obj = json.loads(rsp)
            token = str(obj['access_token'])
            self.access_token = token
            return self.access_token
        except:
            return None

    def get_oauth_userinfo(self):
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,picture,email'
        }
        try:
            rsp = self.do_get(self.API_URL, params)
            datas = json.loads(rsp)
            user = OAuthUser()
            user.nikename = datas['name']
            user.openid = datas['id']
            user.type = 'facebook'
            user.token = self.access_token
            if datas['email']:
                user.email = datas['email']
            if datas['picture'] and datas['picture']['data'] and datas['picture']['data']['url']:
                user.picture = str(datas['picture']['data']['url'])
            return user
        except Exception as e:
            logger.warn(e)
            return None

        """
        params = {
            'input_token': self.access_token,
            'access_token': self.client_id + '|' + self.client_secret
        }
        url = 'https://graph.facebook.com/debug_token'  # + urllib.parse.urlencode(params)
        rsp = self.do_get(url, params)
        try:
            obj = json.loads(rsp)
            userid = str(obj["data"]["user_id"])
            url = 'https://graph.facebook.com/v2.6/' + userid
            params = {'access_token': self.access_token}
            rsp = self.do_get(url, params)
            print(rsp)
        except:
            pass
        """


def get_oauth_apps():
    applications = BaseOauthManager.__subclasses__()
    return list(map(lambda x: x(), applications))


def get_manager_by_type(type):
    applications = get_oauth_apps()
    finds = list(filter(lambda x: x.ICON_NAME.lower() == type.lower(), applications))
    if finds:
        return finds[0]
    return None
