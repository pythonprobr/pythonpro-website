import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def resp(client):
    return client.get(reverse('launch:vip_list'))


def test_status_code(resp):
    assert 200 == resp.status_code


def test_email_field_is_present(resp):
    dj_assert_contains(resp, 'https://python.activehosted.com/f/embed.php?id=2')
