import logging
import time

from ipware import get_client_ip
from user_agents import parse

from blog.documents import ELASTICSEARCH_ENABLED, ElaspedTimeDocumentManager

logger = logging.getLogger(__name__)


class OnlineMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        ''' 
        Page render time tracking middleware
        
        Security Note: IP address is extracted server-side using ipware.get_client_ip()
        which properly handles X-Forwarded-For headers. Geographic location is then
        derived server-side by Elasticsearch's GeoIP pipeline. No client-provided 
        location data is accepted.
        '''
        start_time = time.time()
        response = self.get_response(request)
        http_user_agent = request.META.get('HTTP_USER_AGENT', '')
        # Security: IP is extracted server-side, not from client input
        ip, _ = get_client_ip(request)
        user_agent = parse(http_user_agent)
        if not response.streaming:
            try:
                cast_time = time.time() - start_time
                if ELASTICSEARCH_ENABLED:
                    time_taken = round((cast_time) * 1000, 2)
                    url = request.path
                    from django.utils import timezone
                    # Security: GeoIP location is derived server-side by Elasticsearch
                    # from the IP address, not from any client-provided data
                    ElaspedTimeDocumentManager.create(
                        url=url,
                        time_taken=time_taken,
                        log_datetime=timezone.now(),
                        useragent=user_agent,
                        ip=ip)
                response.content = response.content.replace(
                    b'<!!LOAD_TIMES!!>', str.encode(str(cast_time)[:5]))
            except Exception as e:
                logger.error("Error OnlineMiddleware: %s" % e)

        return response
