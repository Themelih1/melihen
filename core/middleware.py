# core/middleware.py

import logging

logger = logging.getLogger(__name__)

class TrafficLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        ip = request.META.get('REMOTE_ADDR')
        path = request.path
        user = request.user if request.user.is_authenticated else "Anonymous"
        
        logger.info(f"User: {user}, IP: {ip}, Path: {path}")
        return response
