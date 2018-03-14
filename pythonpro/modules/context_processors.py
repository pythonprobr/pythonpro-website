from pythonpro.modules.facade import get_all_modules


def global_settings(request):
    # return any necessary values
    if not request.user.is_authenticated:
        return {}

    return {
        'ALL_MODULES': get_all_modules(),
    }
