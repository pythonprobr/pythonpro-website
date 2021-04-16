import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def resp(client):
    return client.get(reverse('core:podcast'))


def test_status_code(resp):
    assert 200 == resp.status_code


def test_podcast_link(resp):
    dj_assert_contains(resp, 'https://anchor.fm/renzoprocast/embed')
