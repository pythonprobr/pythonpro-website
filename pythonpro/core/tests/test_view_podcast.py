import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def resp(client):
    return client.get(reverse('core:podcast'), secure=True)


def test_status_code(resp):
    assert 200 == resp.status_code


def test_link_on_home(client):
    resp = client.get('/', secure=True)
    dj_assert_contains(resp, reverse('core:podcast'))


def test_podcast_link(resp):
    dj_assert_contains(resp, 'https://anchor.fm/renzoprocast/embed')
