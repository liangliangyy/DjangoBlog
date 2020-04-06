#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: MemcacheStorage.py
@time: 2017/8/27 上午2:42
"""
from werobot.session import SessionStorage
from werobot.utils import json_loads, json_dumps
from DjangoBlog.utils import cache


class MemcacheStorage(SessionStorage):
    def __init__(self, prefix='ws_'):
        self.prefix = prefix
        self.cache = cache

    @property
    def is_available(self):
        value = "1"
        self.set('checkavaliable', value=value)
        return value == self.get('checkavaliable')

    def key_name(self, s):
        return '{prefix}{s}'.format(prefix=self.prefix, s=s)

    def get(self, id):
        id = self.key_name(id)
        session_json = self.cache.get(id) or '{}'
        return json_loads(session_json)

    def set(self, id, value):
        id = self.key_name(id)
        self.cache.set(id, json_dumps(value))

    def delete(self, id):
        id = self.key_name(id)
        self.cache.delete(id)
