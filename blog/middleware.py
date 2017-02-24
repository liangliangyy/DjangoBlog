#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: middleware.py
@time: 2017/1/19 上午12:36
"""

import time
from ipware.ip import get_real_ip
from DjangoBlog.utils import cache


class OnlineMiddleware(object):
    def process_request(self, request):
        self.start_time = time.time()

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        处理当前在线人数
        """
        http_user_agent = request.META.get('HTTP_USER_AGENT', [])
        if 'Spider' in http_user_agent or 'spider' in http_user_agent:
            return

        online_ips = cache.get("online_ips", [])
        if online_ips:
            online_ips = cache.get_many(online_ips).keys()
            online_ips = list(online_ips)
        ip = get_real_ip(request)

        cache.set(ip, 0, 5 * 60)

        if ip not in online_ips:
            online_ips.append(ip)
            s = type(online_ips)
            cache.set("online_ips", online_ips)

    def process_response(self, request, response):
        cast_time = 0.921
        if self.__dict__ and 'start_time' in self.__dict__:
            cast_time = time.time() - self.start_time
        response.content = response.content.replace(b'<!!LOAD_TIMES!!>', str.encode(str(cast_time)[:5]))
        return response
