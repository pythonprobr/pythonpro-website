import operator
from datetime import datetime, timedelta
from os import path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import date
from django.urls import reverse
from model_mommy import mommy

from pythonpro import settings
from pythonpro.cohorts import facade
from pythonpro.cohorts.models import Cohort, LiveClass, Webinar
from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains

_img_path = path.join(settings.BASE_DIR, 'pythonpro', 'core', 'static', 'img', 'instructors', 'renzo-nuccitelli.png')


@pytest.fixture
def cohort(client, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    image = SimpleUploadedFile(name='renzo-nuccitelli.png', content=open(_img_path, 'rb').read(),
                               content_type='image/png')
    cohort = mommy.make(Cohort, slug='guido-van-rossum', students=[user], image=image)
    return cohort


@pytest.fixture
def resp(client, cohort):
    return client.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}), secure=True)


@pytest.fixture
def resp_without_user(client, db):
    image = SimpleUploadedFile(name='renzo-nuccitelli.png', content=open(_img_path, 'rb').read(),
                               content_type='image/png')
    cohort = mommy.make(Cohort, slug='guido-van-rossum', image=image)
    resp = client.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}), secure=True)
    return resp


def test_no_access(resp_without_user):
    """Assert only logged user can acess cohort pages"""
    assert 302 == resp_without_user.status_code


def test_cohort_links_for_logged_user(client, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    image = SimpleUploadedFile(name='renzo-nuccitelli.png', content=open(_img_path, 'rb').read(),
                               content_type='image/png')
    cohorts = mommy.make(Cohort, 4, image=image)
    resp = client.get('/', secure=True)
    for c in cohorts:
        dj_assert_contains(resp, c.get_absolute_url())


@pytest.mark.django_db
def test_cohort_links_not_avaliable_for_no_user(client):
    image = SimpleUploadedFile(name='renzo-nuccitelli.png', content=open(_img_path, 'rb').read(),
                               content_type='image/png')
    cohorts = mommy.make(Cohort, 4, image=image)
    resp = client.get('/', secure=True)
    for c in cohorts:
        dj_assert_not_contains(resp, c.get_absolute_url())


def test_status_code(resp):
    assert 200 == resp.status_code


@pytest.mark.parametrize('property_name', 'title mail_list forum_post'.split())
def test_cohort_propeties(cohort, resp, property_name):
    dj_assert_contains(resp, getattr(cohort, property_name))


def test_cohort_img(cohort: Cohort, resp):
    dj_assert_contains(resp, cohort.image.url)


def test_cohort_start(cohort: Cohort, resp):
    dj_assert_contains(resp, date(cohort.start))


def test_cohort_end(cohort: Cohort, resp):
    dj_assert_contains(resp, date(cohort.end))


@pytest.fixture
def live_classes(cohort):
    now = datetime.now()
    return [
        mommy.make(LiveClass, cohort=cohort, vimeo_id=str(i), start=now + timedelta(days=i)) for i in range(100, 105)
    ]


@pytest.fixture
def resp_with_classes(live_classes, cohort, client):
    return client.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}), secure=True)


def test_live_classes_are_sorted(live_classes: list, cohort):
    live_classes.sort(key=operator.attrgetter('start'))
    db_cohort = facade.find_cohort(slug=cohort.slug)
    assert live_classes == db_cohort.classes


def test_live_classes_datetime(resp_with_classes, live_classes):
    for live_class in live_classes:
        dj_assert_contains(resp_with_classes, date(live_class.start))


def test_live_classes_vimeo(resp_with_classes, live_classes):
    for live_class in live_classes:
        dj_assert_contains(resp_with_classes, live_class.vimeo_id)


@pytest.fixture
def webinars(cohort):
    now = datetime.now()
    return [
        mommy.make(Webinar, cohort=cohort, vimeo_id=str(i), start=now + timedelta(days=i)) for i in range(100, 105)
    ]


@pytest.fixture
def resp_with_webinars(webinars, cohort, client):
    return client.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}), secure=True)


def test_webinars_are_sorted(webinars: list, cohort):
    webinars.sort(key=operator.attrgetter('start'))
    db_cohort = facade.find_cohort(slug=cohort.slug)
    assert webinars == db_cohort.webinars


def test_webinars_datetime(resp_with_webinars, webinars):
    for live_class in webinars:
        dj_assert_contains(resp_with_webinars, date(live_class.start))


@pytest.mark.parametrize('property_name', 'speaker speaker_title title vimeo_id'.split())
def test_webinars_vimeo(resp_with_webinars, webinars, property_name):
    for webnar in webinars:
        dj_assert_contains(resp_with_webinars, getattr(webnar, property_name))
