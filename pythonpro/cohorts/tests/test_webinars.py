import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains


@pytest.fixture
def resp(client_with_user, webinars):
    return client_with_user.get(reverse('cohorts:webinars'), secure=True)


def test_link_for_logged_user(client_with_user):
    resp = client_with_user.get('/', secure=True)
    dj_assert_contains(resp, reverse('cohorts:webinars'))


def test_link_unavailable_for_non_users(client):
    resp = client.get('/', secure=True)
    dj_assert_not_contains(resp, reverse('cohorts:webinars'))


def test_status_code(resp):
    assert resp.status_code == 200


@pytest.mark.parametrize('property_name', 'speaker speaker_title title description'.split())
def test_basic_contents(resp, webinars, property_name):
    for webinar in webinars:
        dj_assert_contains(resp, getattr(webinar, property_name))


def test_absolute_url(resp, webinars):
    for webinar in webinars:
        dj_assert_contains(resp, webinar.get_absolute_url())
