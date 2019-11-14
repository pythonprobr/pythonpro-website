from django.utils.deprecation import MiddlewareMixin

from pythonpro.analytics.facade import get_or_create_session


class AnalyticsMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request = get_or_create_session(request)
        return self.get_response(request)