import operator
from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from model_bakery import baker

from pythonpro.cohorts import facade
from pythonpro.cohorts.models import LiveClass, Webinar
from pythonpro.cohorts.tests.conftest import img_path


def test_str(cohort):
    assert str(cohort) == f'Turma: {cohort.title}'


@pytest.fixture
def recorded_live_classes(cohort, fake):
    now = timezone.now()
    return [
        baker.make(
            LiveClass,
            cohort=cohort,
            vimeo_id=str(i),
            start=now + timedelta(days=i),
            description=fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None))
        for i in range(100, 105)
    ]


@pytest.fixture
def future_live_classes(cohort, fake):
    """
    No recorded live classes (missing vimeo id)
    :param cohort:
    :param fake:
    :return:
    """
    now = timezone.now()
    return [
        baker.make(
            LiveClass,
            cohort=cohort,
            vimeo_id='',
            start=now + timedelta(days=i),
            description=fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None))
        for i in range(100, 105)
    ]


def test_live_classes_are_sorted(recorded_live_classes, cohort):
    recorded_live_classes.sort(key=operator.attrgetter('start'))
    db_cohort = facade.find_cohort(slug=cohort.slug)
    assert recorded_live_classes == db_cohort.classes


@pytest.fixture
def recorded_webinars(cohort):
    now = timezone.now()
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    return [
        baker.make(Webinar, cohort=cohort, vimeo_id=str(i), image=image, start=now + timedelta(days=i)) for i in
        range(100, 105)
    ]


@pytest.fixture
def future_webinars(cohort):
    now = timezone.now()
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    return [
        baker.make(Webinar, cohort=cohort, vimeo_id='', image=image, start=now + timedelta(days=i)) for i in
        range(100, 105)
    ]


def test_recorded_webinars_in_cohort(recorded_webinars, future_webinars, cohort):
    cohort = facade.find_cohort(cohort.slug)
    assert cohort.recorded_webinars == recorded_webinars


def test_future_webinars_in_cohort(recorded_webinars, future_webinars, cohort):
    cohort = facade.find_cohort(cohort.slug)
    assert cohort.future_webinars == future_webinars


def test_webnars_are_sorted(recorded_webinars: list, cohort):
    recorded_webinars.sort(key=operator.attrgetter('start'))
    db_cohort = facade.find_cohort(slug=cohort.slug)
    assert recorded_webinars == db_cohort.webinars
