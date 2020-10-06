import operator
from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from pythonpro.cohorts import facade
from pythonpro.cohorts.models import Cohort, LiveClass, Webinar
from pythonpro.cohorts.tests.conftest import img_path
from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains


@pytest.fixture
def resp(client_with_member, cohort):
    return client_with_member.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}))


@pytest.fixture
def resp_without_user(client, db):
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    cohort = baker.make(Cohort, slug='guido-van-rossum', image=image)
    resp = client.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}))
    return resp


def test_no_access(resp_without_user):
    """Assert only logged user can acess cohort pages"""
    assert 302 == resp_without_user.status_code


def test_cohort_links_for_logged_user(client, django_user_model):
    user = baker.make(django_user_model)
    client.force_login(user)
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    cohorts = baker.make(Cohort, 4, image=image)
    resp = client.get(reverse('dashboard:home'))
    for c in cohorts:
        dj_assert_contains(resp, c.get_absolute_url())


@pytest.mark.django_db
def test_cohort_links_not_avaliable_for_no_user(client):
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    cohorts = baker.make(Cohort, 4, image=image)
    resp = client.get('/')
    for c in cohorts:
        dj_assert_not_contains(resp, c.get_absolute_url())


def test_status_code(resp):
    assert 200 == resp.status_code


def test_str(cohort):
    assert str(cohort) == f'Turma: {cohort.title}'


@pytest.mark.parametrize('property_name', 'title forum_post'.split())
def test_cohort_properties(cohort, resp, property_name):
    dj_assert_contains(resp, getattr(cohort, property_name))


def test_cohort_img(cohort: Cohort, resp):
    dj_assert_contains(resp, cohort.image.url)


def test_cohort_start(cohort: Cohort, resp):
    dj_assert_contains(resp, date(cohort.start))


def test_cohort_end(cohort: Cohort, resp):
    dj_assert_contains(resp, date(cohort.end))


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


@pytest.fixture
def resp_with_classes(recorded_live_classes, future_live_classes, cohort, client_with_member):
    return client_with_member.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}))


def test_live_classes_are_sorted(recorded_live_classes, cohort):
    recorded_live_classes.sort(key=operator.attrgetter('start'))
    db_cohort = facade.find_cohort(slug=cohort.slug)
    assert recorded_live_classes == db_cohort.classes


@pytest.mark.freeze_time('2019-01-01 18:00:00')
def test_live_classes_datetime(resp_with_classes, recorded_live_classes):
    for live_class in recorded_live_classes:
        dj_assert_contains(resp_with_classes, date(live_class.start))


def test_live_classes_descriptions(resp_with_classes, recorded_live_classes):
    for live_class in recorded_live_classes:
        dj_assert_contains(resp_with_classes, live_class.description)


def test_recorded_live_classes_urls_are_present(resp_with_classes, recorded_live_classes):
    for live_class in recorded_live_classes:
        dj_assert_contains(resp_with_classes, live_class.get_absolute_url())


def test_future_live_classes_urls_are_absent(resp_with_classes, future_live_classes):
    for live_class in future_live_classes:
        dj_assert_not_contains(resp_with_classes, live_class.get_absolute_url())


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


@pytest.fixture
def resp_with_webnars(recorded_webinars, future_webinars, cohort, client_with_member):
    return client_with_member.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}))


def test_webnars_are_sorted(recorded_webinars: list, cohort):
    recorded_webinars.sort(key=operator.attrgetter('start'))
    db_cohort = facade.find_cohort(slug=cohort.slug)
    assert recorded_webinars == db_cohort.webinars


@pytest.mark.freeze_time('2019-01-01 18:00:00')
def test_webnars_datetime(resp_with_webnars, recorded_webinars):
    for webnar in recorded_webinars:
        dj_assert_contains(resp_with_webnars, date(webnar.start))


@pytest.mark.parametrize('property_name', 'speaker speaker_title title'.split())
def test_webnars_vimeo(resp_with_webnars, recorded_webinars, property_name):
    for webnar in recorded_webinars:
        dj_assert_contains(resp_with_webnars, getattr(webnar, property_name))


def test_recorded_webnars_url_are_present(resp_with_webnars, recorded_webinars):
    for webnar in recorded_webinars:
        dj_assert_contains(resp_with_webnars, webnar.get_absolute_url())


def test_future_webnars_url_are_absent(resp_with_webnars, future_webinars):
    for webnar in future_webinars:
        dj_assert_not_contains(resp_with_webnars, webnar.get_absolute_url())
