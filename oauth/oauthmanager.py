#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: oauthmanager.py
@time: 2016/11/26 下午5:09
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from oauth.models import OAuthUser, OAuthConfig
from django.conf import settings
import requests
import json
import logging
import urllib.parse
from DjangoBlog.utils import parse_dict_to_url, cache_decorator

logger = logging.getLogger(__name__)


class OAuthAccessTokenException(Exception):
    '''
    oauth授权失败异常
    '''


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

    def do_get(self, url, params, headers=None):
        rsp = requests.get(url=url, params=params, headers=headers)
        logger.info(rsp.text)
        return rsp.text

    def do_post(self, url, params, headers=None):
        rsp = requests.post(url, params, headers=headers)
        logger.info(rsp.text)
        return rsp.text

    def get_config(self):
        value = OAuthConfig.objects.filter(type=self.ICON_NAME)
        return value[0] if value else None


class WBOauthManager(BaseOauthManager):
    AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
    TOKEN_URL = 'https://api.weibo.com/oauth2/access_token'
    API_URL = 'https://api.weibo.com/2/users/show.json'
    ICON_NAME = 'weibo'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(
            WBOauthManager,
            self).__init__(
            access_token=access_token,
            openid=openid)

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

        obj = json.loads(rsp)
        if 'access_token' in obj:
            self.access_token = str(obj['access_token'])
            self.openid = str(obj['uid'])
            return self.get_oauth_userinfo()
        else:
            raise OAuthAccessTokenException(rsp)

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
            user.matedata = rsp
            user.picture = datas['avatar_large']
            user.nikename = datas['screen_name']
            user.openid = datas['id']
            user.type = 'weibo'
            user.token = self.access_token
            if 'email' in datas and datas['email']:
                user.email = datas['email']
            return user
        except Exception as e:
            logger.error(e)
            logger.error('weibo oauth error.rsp:' + rsp)
            return None


class GoogleOauthManager(BaseOauthManager):
    AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
    API_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
    ICON_NAME = 'google'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(
            GoogleOauthManager,
            self).__init__(
            access_token=access_token,
            openid=openid)

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

        if 'access_token' in obj:
            self.access_token = str(obj['access_token'])
            self.openid = str(obj['id_token'])
            logger.info(self.ICON_NAME + ' oauth ' + rsp)
            return self.access_token
        else:
            raise OAuthAccessTokenException(rsp)

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
            user.matedata = rsp
            user.picture = datas['picture']
            user.nikename = datas['name']
            user.openid = datas['sub']
            user.token = self.access_token
            user.type = 'google'
            if datas['email']:
                user.email = datas['email']
            return user
        except Exception as e:
            logger.error(e)
            logger.error('google oauth error.rsp:' + rsp)
            return None


class GitHubOauthManager(BaseOauthManager):
    AUTH_URL = 'https://github.com/login/oauth/authorize'
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    API_URL = 'https://api.github.com/user'
    ICON_NAME = 'github'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(
            GitHubOauthManager,
            self).__init__(
            access_token=access_token,
            openid=openid)

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

        from urllib import parse
        r = parse.parse_qs(rsp)
        if 'access_token' in r:
            self.access_token = (r['access_token'][0])
            return self.access_token
        else:
            raise OAuthAccessTokenException(rsp)

    def get_oauth_userinfo(self):

        rsp = self.do_get(self.API_URL, params={}, headers={
            "Authorization": "token " + self.access_token
        })
        try:
            datas = json.loads(rsp)
            user = OAuthUser()
            user.picture = datas['avatar_url']
            user.nikename = datas['name']
            user.openid = datas['id']
            user.type = 'github'
            user.token = self.access_token
            user.matedata = rsp
            if 'email' in datas and datas['email']:
                user.email = datas['email']
            return user
        except Exception as e:
            logger.error(e)
            logger.error('github oauth error.rsp:' + rsp)
            return None


class FaceBookOauthManager(BaseOauthManager):
    AUTH_URL = 'https://www.facebook.com/v2.10/dialog/oauth'
    TOKEN_URL = 'https://graph.facebook.com/v2.10/oauth/access_token'
    API_URL = 'https://graph.facebook.com/me'
    ICON_NAME = 'facebook'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(
            FaceBookOauthManager,
            self).__init__(
            access_token=access_token,
            openid=openid)

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

        obj = json.loads(rsp)
        if 'access_token' in obj:
            token = str(obj['access_token'])
            self.access_token = token
            return self.access_token
        else:
            raise OAuthAccessTokenException(rsp)

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
            user.matedata = rsp
            if 'email' in datas and datas['email']:
                user.email = datas['email']
            if 'picture' in datas and datas['picture'] and datas['picture']['data'] and datas['picture']['data']['url']:
                user.picture = str(datas['picture']['data']['url'])
            return user
        except Exception as e:
            logger.error(e)
            return None


class QQOauthManager(BaseOauthManager):
    AUTH_URL = 'https://graph.qq.com/oauth2.0/authorize'
    TOKEN_URL = 'https://graph.qq.com/oauth2.0/token'
    API_URL = 'https://graph.qq.com/user/get_user_info'
    OPEN_ID_URL = 'https://graph.qq.com/oauth2.0/me'
    ICON_NAME = 'qq'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(
            QQOauthManager,
            self).__init__(
            access_token=access_token,
            openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.callback_url + '&next_url=' + nexturl,
        }
        url = self.AUTH_URL + "?" + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.callback_url
        }
        rsp = self.do_get(self.TOKEN_URL, params)
        if rsp:
            d = urllib.parse.parse_qs(rsp)
            if 'access_token' in d:
                token = d['access_token']
                self.access_token = token
                return token
        else:
            raise OAuthAccessTokenException(rsp)

    def get_open_id(self):
        if self.is_access_token_set:
            params = {
                'access_token': self.access_token
            }
            rsp = self.do_get(self.OPEN_ID_URL, params)
            if rsp:
                rsp = rsp.replace(
                    'callback(', '').replace(
                    ')', '').replace(
                    ';', '')
                obj = json.loads(rsp)
                openid = str(obj['openid'])
                self.openid = openid
                return openid

    def get_oauth_userinfo(self):
        openid = self.get_open_id()
        if openid:
            params = {
                'access_token': self.access_token,
                'oauth_consumer_key': self.client_id,
                'openid': self.openid
            }
            rsp = self.do_get(self.API_URL, params)
            logger.info(rsp)
            obj = json.loads(rsp)
            user = OAuthUser()
            user.nikename = obj['nickname']
            user.openid = openid
            user.type = 'qq'
            user.token = self.access_token
            user.matedata = rsp
            if 'email' in obj:
                user.email = obj['email']
            if 'figureurl' in obj:
                user.picture = str(obj['figureurl'])
            return user


@cache_decorator(expiration=100 * 60)
def get_oauth_apps():
    configs = OAuthConfig.objects.filter(is_enable=True).all()
    if not configs:
        return []
    configtypes = [x.type for x in configs]
    applications = BaseOauthManager.__subclasses__()
    apps = [x() for x in applications if x().ICON_NAME.lower() in configtypes]
    return apps


def get_manager_by_type(type):
    applications = get_oauth_apps()
    if applications:
        finds = list(
            filter(
                lambda x: x.ICON_NAME.lower() == type.lower(),
                applications))
        if finds:
            return finds[0]
    return None
