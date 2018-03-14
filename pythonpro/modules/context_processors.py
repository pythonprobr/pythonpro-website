from pythonpro.modules import models


def global_settings(request):
    # return any necessary values
    dct = {
        'ALL_MODULES': list(models.ALL.values()),
    }
    return dct
