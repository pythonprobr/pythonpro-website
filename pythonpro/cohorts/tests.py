from os import path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import date
from django.urls import reverse
from model_mommy import mommy

from pythonpro import settings
from pythonpro.cohorts.models import Cohort
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
    resp = client.get(reverse('cohorts:detail', kwargs={'slug': cohort.slug}), secure=True)
    return resp


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
