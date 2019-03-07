from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.cohorts.models import Cohort, LiveClass, Webinar
from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def live_class(db, cohort, fake) -> LiveClass:
    now = datetime.utcnow()
    return mommy.make(
        LiveClass,
        cohort=cohort,
        vimeo_id='1212',
        start=now + timedelta(days=1),
        description=fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)
    )


@pytest.fixture
def resp(client_with_user, live_class: Webinar):
    return client_with_user.get(reverse('cohorts:live_class', kwargs={'pk': live_class.id}), secure=True)


def test_logged_user(resp):
    assert resp.status_code == 200


def test_link_unavailable_for_non_users(client):
    resp = client.get(reverse('cohorts:live_class', kwargs={'pk': 1}), secure=True)
    assert resp.status_code == 302


@pytest.mark.parametrize('property_name', 'description vimeo_id discourse_topic_id'.split())
def test_basic_contents(resp, live_class, property_name):
    dj_assert_contains(resp, getattr(live_class, property_name))


def test_cohort_title(cohort, resp):
    dj_assert_contains(resp, cohort.title)


def test_cohort_url(cohort: Cohort, resp):
    dj_assert_contains(resp, cohort.get_absolute_url())
