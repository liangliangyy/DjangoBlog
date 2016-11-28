from django.shortcuts import render

# Create your views here.
from .oauthmanager import WBOauthManager
from django.conf import settings
from django.http import HttpResponse


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
