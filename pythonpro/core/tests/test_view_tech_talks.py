import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def resp(client):
    return client.get(reverse('core:tech_talks'))


def test_status_code(resp):
    assert 200 == resp.status_code


def test_link_on_home(client):
    resp = client.get('/')
    dj_assert_contains(resp, reverse('core:tech_talks'))
