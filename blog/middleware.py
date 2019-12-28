#!/usr/bin/env python

import datetime
import time
from ipware.ip import get_real_ip
from DjangoBlog.utils import cache
from blog.documents import ELASTICSEARCH_ENABLED, ElaspedTimeDocumentManager


class OnlineMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        http_user_agent = request.META.get('HTTP_USER_AGENT', [])
        if 'Spider' in http_user_agent or 'spider' in http_user_agent:
            return response
        try:
            cast_time = time.time() - start_time
            if ELASTICSEARCH_ENABLED:
                time_taken = round((cast_time) * 1000, 2)
                url = request.path
                from django.utils import timezone

                ElaspedTimeDocumentManager.create(url=url, time_taken=time_taken, log_datetime=timezone.now(),
                                                  type='blog', useragent=http_user_agent)
            response.content = response.content.replace(b'<!!LOAD_TIMES!!>', str.encode(str(cast_time)[:5]))
        except:
            pass
        return response
