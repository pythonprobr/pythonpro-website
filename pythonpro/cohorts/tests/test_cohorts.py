import operator
from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils import timezone
from model_mommy import mommy

from pythonpro.cohorts import facade
from pythonpro.cohorts.models import Cohort, LiveClass
from pythonpro.cohorts.tests.conftest import img_path
from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains


@pytest.fixture
def resp(client_with_member, cohort):
    return client_with_member.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}), secure=True)


@pytest.fixture
def resp_without_user(client, db):
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
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
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    cohorts = mommy.make(Cohort, 4, image=image)
    resp = client.get('/', secure=True)
    for c in cohorts:
        dj_assert_contains(resp, c.get_absolute_url())


@pytest.mark.django_db
def test_cohort_links_not_avaliable_for_no_user(client):
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
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
def live_classes(cohort, fake):
    now = timezone.now()
    return [
        mommy.make(
            LiveClass,
            cohort=cohort,
            vimeo_id=str(i),
            start=now + timedelta(days=i),
            description=fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None))
        for i in range(100, 105)
    ]


@pytest.fixture
def resp_with_classes(live_classes, cohort, client_with_member):
    return client_with_member.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}), secure=True)


def test_live_classes_are_sorted(live_classes: list, cohort):
    live_classes.sort(key=operator.attrgetter('start'))
    db_cohort = facade.find_cohort(slug=cohort.slug)
    assert live_classes == db_cohort.classes


def test_live_classes_datetime(resp_with_classes, live_classes):
    for live_class in live_classes:
        dj_assert_contains(resp_with_classes, date(live_class.start))


def test_live_classes_descriptions(resp_with_classes, live_classes):
    for live_class in live_classes:
        dj_assert_contains(resp_with_classes, live_class.description)


def test_live_classes_urls(resp_with_classes, live_classes):
    for live_class in live_classes:
        dj_assert_contains(resp_with_classes, live_class.get_absolute_url())


@pytest.fixture
def resp_with_webinars(webinars, cohort, client_with_member):
    return client_with_member.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}), secure=True)


def test_webinars_are_sorted(webinars: list, cohort):
    webinars.sort(key=operator.attrgetter('start'))
    db_cohort = facade.find_cohort(slug=cohort.slug)
    assert webinars == db_cohort.webinars


def test_webinars_datetime(resp_with_webinars, webinars):
    for live_class in webinars:
        dj_assert_contains(resp_with_webinars, date(live_class.start))


@pytest.mark.parametrize('property_name', 'speaker speaker_title title'.split())
def test_webinars_vimeo(resp_with_webinars, webinars, property_name):
    for webnar in webinars:
        dj_assert_contains(resp_with_webinars, getattr(webnar, property_name))
