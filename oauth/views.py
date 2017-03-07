from django.shortcuts import render

# Create your views here.
from .oauthmanager import WBOauthManager, GoogleOauthManager, get_manager_by_type
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from .models import oauthuser
from django.contrib.auth import login


def authorize(request):
    manager = None
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    code = request.GET.get('code', None)
    rsp = manager.get_access_token_by_code(code)
    if not rsp:
        return HttpResponseRedirect(manager.get_authorization_url())
    user = manager.get_oauth_userinfo()
    author = None
    if user:
        email = user.email
        if email:
            author = get_user_model().objects.get(email=email)
            if not author:
                author = get_user_model().objects.create_user(username=user["name"], email=email)
            user.author = author
            user.save()
            login(request, author)
            return HttpResponseRedirect('/')
        if not email:
            author = get_user_model().objects.create_user(username=user["name"], email=email)


"""
def wbauthorize(request, sitename):
    manager = WBOauthManager(client_id=settings.OAHUTH['sina']['appkey'],
                             client_secret=settings.OAHUTH['sina']['appsecret'],
                             callback_url=settings.OAHUTH['sina']['callbackurl'])
    code = request.GET.get('code', None)
    rsp = manager.get_access_token_by_code(code)
    print(rsp)
    return HttpResponse(rsp)


def wboauthurl(request):
    manager = WBOauthManager(client_id=settings.OAHUTH['sina']['appkey'],
                             client_secret=settings.OAHUTH['sina']['appsecret'],
                             callback_url=settings.OAHUTH['sina']['callbackurl'])
    url = manager.get_authorization_url()
    return HttpResponse(url)


def googleoauthurl(request):
    manager = GoogleOauthManager()
    url = manager.get_authorization_url()
    return HttpResponse(url)


def googleauthorize(request):
    manager = GoogleOauthManager()
    code = request.GET.get('code', None)
    rsp = manager.get_access_token_by_code(code)
    if not rsp:
        return HttpResponseRedirect(manager.get_authorization_url())
    user = manager.get_oauth_userinfo()
    if user:
        email = user['email']
        if email:
            author = get_user_model().objects.get(email=email)
            if not author:
                author = get_user_model().objects.create_user(username=user["name"], email=email)
            if not GoogleUserInfo.objects.filter(author_id=author.pk):
                userinfo = GoogleUserInfo()
                userinfo.author = author
                userinfo.picture = user["picture"]
                userinfo.token = manager.access_token
                userinfo.openid = manager.openid
                userinfo.nikename = user["name"]
                userinfo.save()
            login(request, author)
        else:
            pass
    return HttpResponseRedirect('/')
"""
