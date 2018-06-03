from pythonpro.cohorts.facade import get_all_cohorts_desc


def global_settings(request):
    # return any necessary values
    if not request.user.is_authenticated:
        return {}

    return {
        'ALL_COHORTS': get_all_cohorts_desc(),
    }
