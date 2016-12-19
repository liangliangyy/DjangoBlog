#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.org/
@software: PyCharm
@file: wordpress_helper.py
@time: 2016/12/10 上午9:43
"""

import pymysql
import urllib
from urllib.parse import quote_plus, quote
import os


class wordpress_helper():
    def __init__(self):
        USER = os.environ.get('DJANGO_MYSQL_USER')
        PASSWORD = os.environ.get('DJANGO_MYSQL_PASSWORD')
        HOST = os.environ.get('DJANGO_MYSQL_HOST')
        self.db = pymysql.connect(HOST, USER, PASSWORD, 'djangoblog')

    def get_postid_by_postname(self, postname):
        sql = "SELECT id from wordpress.wp_posts WHERE post_name='%s' " % quote(postname)
        cursor = self.db.cursor()
        cursor.execute(sql)
        try:
            result = cursor.fetchone()
            return result[0]
        except:
            return 0


if __name__ == '__main__':
    name = '使用nginxgunicornvirtualenvsupervisor来部署django项目'
    helper = wordpress_helper()
    post_id = helper.get_postid_by_postname(name)
    print(post_id)
