import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.redirector.models import Redirect
from pythonpro.redirector.facade import get_redirect_url


@pytest.fixture
def redirect(db):
    return mommy.make(Redirect, url='https://google.com')


@pytest.fixture
def resp(client, redirect):
    return client.get(reverse('redirector:redirect', kwargs={'slug': redirect.slug}), secure=True)


def test_status_code_should_return_302(resp):
    assert resp.status_code == 302
