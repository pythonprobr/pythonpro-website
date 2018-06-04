from django.db.models import Prefetch

from pythonpro.cohorts.models import Cohort as _Cohort, LiveClass


def get_all_cohorts_desc():
    return tuple(_Cohort.objects.order_by('-start'))


def find_cohort(slug):
    return _Cohort.objects.filter(slug=slug).prefetch_related(Prefetch(
        'liveclass_set',
        queryset=LiveClass.objects.order_by('start'),
        to_attr='classes'
    )).get()
