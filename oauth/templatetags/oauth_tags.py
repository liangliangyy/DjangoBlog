#!/usr/bin/env python

from oauth.oauthmanager import get_oauth_apps
from django.urls import reverse
from django import template
from django.conf import settings

register = template.Library()
import logging
logger = logging.getLogger(__name__)

@register.inclusion_tag('oauth/oauth_applications.html')
def load_oauth_applications(request):
    applications = get_oauth_apps()
    if applications:
        baseurl = reverse('oauth:oauthlogin')
        path = request.get_full_path()

        apps = list(map(lambda x: (x.ICON_NAME,
                                   '{baseurl}?type={type}&next_url={next}'
                                   .format(baseurl=baseurl, type=x.ICON_NAME, next=path)), applications))
    else:
        apps = []
    return {
        'apps': apps
    }
