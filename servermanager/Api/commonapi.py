#!/usr/bin/env python

import requests
import json
import logging

logger = logging.getLogger(__name__)


class TuLing():
    def __init__(self):
        self.__key__ = '2f1446eb0321804291b0a1e217c25bb5'
        self.__appid__ = 137762

    def __build_req_url(self, content):
        return 'http://www.tuling123.com/openapi/api?key=%s&info=%s&userid=%s' % (
            self.__key__, content, self.__appid__)

    def UserAgent(self, url):
        rsp = requests.get(url)
        return rsp.content

    def getdata(self, content):
        try:
            requrl = self.__build_req_url(content)
            res = self.UserAgent(requrl).decode('utf-8')

            jsons = json.loads(res, encoding='utf-8')
            if str(jsons["code"]) == '100000':
                return jsons["text"]
        except Exception as e:
            logger.error(e)
        return "К сожалению, что-то пошло не так."
