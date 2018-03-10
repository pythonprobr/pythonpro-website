from django.conf import settings


def global_settings(request):
    # return any necessary values
    dct = {'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL, }
    return dct
