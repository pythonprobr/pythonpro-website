from pythonpro.courses.models import courses


def global_settings(request):
    # return any necessary values
    dct = {
        'ALL_COURSES': list(courses.ALL.values()),
    }
    return dct
