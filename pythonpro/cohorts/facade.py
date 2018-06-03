from pythonpro.cohorts.models import Cohort as _Cohort


def get_all_cohorts_desc():
    return tuple(_Cohort.objects.order_by('-start'))
