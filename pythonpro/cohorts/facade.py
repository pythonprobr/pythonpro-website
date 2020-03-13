from django.db.models import Prefetch as _Prefetch
from django.urls import reverse

from pythonpro.cohorts.models import Cohort as _Cohort, CohortStudent, LiveClass as _LiveClass, Webinar as _Webinar

__all__ = [
    'get_all_cohorts_desc',
    'find_cohort',
    'find_most_recent_cohort',
    'calculate_most_recent_cohort_path',
    'find_webinars',
    'find_webinar',
    'find_live_class',
]


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


def find_most_recent_cohort():
    return _Cohort.objects.order_by('-start').first()


def calculate_most_recent_cohort_path() -> str:
    slug_dct = _Cohort.objects.order_by('-start').values('slug').first()
    return reverse('modules:detail', kwargs=slug_dct)


def find_webinars():
    """
    Retrieve Webinars from database ordered by date desc
    :return: Tuple of webinars
    """
    return tuple(_Webinar.objects.order_by('-start'))


def find_recorded_webinars():
    """
    Retrieve recorded Webinars from database ordered by date desc.
    A recorded Webinar has vimeo_id not empty
    :return: Tuple of webinars
    """
    return tuple(_Webinar.objects.order_by('-start').exclude(vimeo_id__exact=''))


def find_webinar(slug):
    """
    Retrieve Webinar by its slug
    :return: Webinar
    """
    return _Webinar.objects.filter(slug=slug).get()


def find_live_class(pk):
    """
    Find Live Class by its PK, selecting related cohort
    :param pk:
    :return:
    """
    return _LiveClass.objects.select_related('cohort').get(pk=pk)


def subscribe_to_last_cohort(user):
    ch = CohortStudent(user=user, cohort=find_most_recent_cohort())
    ch.save()
    return ch
