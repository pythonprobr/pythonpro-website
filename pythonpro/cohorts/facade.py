from django.db.models import Prefetch as _Prefetch

from pythonpro.cohorts.models import Cohort as _Cohort, LiveClass as _LiveClass, Webinar as _Webinar


def get_all_cohorts_desc():
    return tuple(_Cohort.objects.order_by('-start'))


def find_cohort(slug):
    return _Cohort.objects.filter(slug=slug).prefetch_related(
        _Prefetch(
            'liveclass_set',
            queryset=_LiveClass.objects.order_by('start'),
            to_attr='classes'
        )
    ).prefetch_related(
        _Prefetch(
            'webinar_set',
            queryset=_Webinar.objects.order_by('start'),
            to_attr='webinars'
        )
    ).get()


def find_webinars():
    """
    Retrieve Webinars from database ordered by date desc
    :return: List of webinars
    """
    return tuple(_Webinar.objects.order_by('-start'))


def find_webinar(slug):
    """
    Retrieve Webinar by its slug
    :return: Webinar
    """
    return _Webinar.objects.filter(slug=slug).get()
