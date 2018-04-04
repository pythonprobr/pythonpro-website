from django.conf import settings


def global_settings(request):
    # return any necessary values
    dct = {
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
        'DISCOURSE_BASE_URL': settings.DISCOURSE_BASE_URL,
    }
    return dct
