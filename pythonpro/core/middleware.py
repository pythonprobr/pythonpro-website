from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponseRedirect


class SSLMiddleware:
    debug_flag = False

    def __init__(self, get_response):
        if settings.DEBUG or self.debug_flag:
            # hack because pytest set debug to false
            # https://stackoverflow.com/questions/40496051/pytest-and-django-settings-runtime-changes
            SSLMiddleware.debug_flag = True
            raise MiddlewareNotUsed('Debug is True')
        self.get_response = get_response

    def __call__(self, request):
        if not any([request.is_secure(), request.META.get("HTTP_X_FORWARDED_PROTO", "") == 'https']):
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace("http://", "https://")
            return HttpResponseRedirect(secure_url)
        return self.get_response(request)
