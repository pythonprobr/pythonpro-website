import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.redirector.models import Redirect


@pytest.fixture
def redirect(db):
    return mommy.make(Redirect)


@pytest.fixture
def resp(client, redirect):
    return client.get(reverse('redirector:redirect', kwargs={'slug': redirect.slug}), secure=True)


def test_status_code(resp):
    assert resp.status_code == 200


def test_redirect_js(resp, redirect):
    dj_assert_contains(resp, f'window.location.replace("{redirect.url}")')
