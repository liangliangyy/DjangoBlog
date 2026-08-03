#!/usr/bin/env python
# encoding: utf-8

"""
Simple rate limiting for authentication endpoints
Uses Django cache to track attempts
"""

import logging
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def ratelimit(key_prefix='ratelimit', rate='5/m', method='POST'):
    """
    Rate limiting decorator
    
    Args:
        key_prefix: Prefix for cache key
        rate: Rate limit string (e.g., '5/m' for 5 requests per minute)
        method: HTTP method to rate limit (default: POST)
    
    Usage:
        @ratelimit(key_prefix='login', rate='5/m')
        def my_view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapped(request, *args, **kwargs):
            # Only rate limit specified method
            if request.method != method:
                return func(request, *args, **kwargs)
            
            # Parse rate limit
            try:
                num_requests, period = rate.split('/')
                num_requests = int(num_requests)
                
                # Convert period to seconds
                if period == 'm':
                    timeout = 60
                elif period == 'h':
                    timeout = 3600
                elif period == 'd':
                    timeout = 86400
                else:
                    timeout = int(period)  # Assume it's already in seconds
            except (ValueError, AttributeError):
                logger.error(f"Invalid rate format: {rate}")
                # If rate format is invalid, don't rate limit
                return func(request, *args, **kwargs)
            
            # Get client identifier (IP address)
            ip = get_client_ip(request)
            cache_key = f'{key_prefix}:{ip}'
            
            # Get current request count
            request_count = cache.get(cache_key, 0)
            
            if request_count >= num_requests:
                logger.warning(
                    f'Rate limit exceeded for {key_prefix} from IP {ip}: '
                    f'{request_count} requests'
                )
                return HttpResponse(
                    _('Too many requests. Please try again later.'),
                    status=429
                )
            
            # Increment request count
            if request_count == 0:
                # First request, set with timeout
                cache.set(cache_key, 1, timeout)
            else:
                # Increment existing count
                cache.incr(cache_key)
            
            return func(request, *args, **kwargs)
        
        return wrapped
    return decorator
