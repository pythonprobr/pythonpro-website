from pythonpro.modules.models import modules


def global_settings(request):
    # return any necessary values
    dct = {
        'ALL_MODULES': list(modules.ALL.values()),
    }
    return dct
