#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: robot.py
@time: 2017/8/27 上午1:55
"""

from werobot import WeRoBot
import re
from werobot.replies import ArticlesReply, MusicReply, ImageReply
from .MemcacheStorage import MemcacheStorage

robot = WeRoBot(token='lylinux', enable_session=True)

robot.config['SESSION_STORAGE'] = MemcacheStorage()


@robot.handler
def hello(message, session):
    count = 0
    if 'count' in session:
        count = session['count']
    count += 1
    session['count'] = count
    return str(count)
