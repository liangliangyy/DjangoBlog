import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SpiderNotify():
    @staticmethod
    def baidu_notify(urls):
        try:
            data = '\n'.join(urls)
            result = requests.post(settings.BAIDU_NOTIFY_URL, data=data)
            logger.info(result.text)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def notify(url):
        SpiderNotify.baidu_notify(url)
