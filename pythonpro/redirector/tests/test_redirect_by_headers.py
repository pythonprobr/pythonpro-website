import pytest
from django.urls import reverse
from model_bakery import baker

from pythonpro.redirector.models import Redirect


@pytest.fixture
def redirect(db):
    return baker.make(Redirect, url='https://google.com')


@pytest.fixture
def resp(client, redirect):
    return client.get(reverse('redirector:redirect', kwargs={'slug': redirect.slug}))


def test_status_code_should_return_302(resp):
    assert resp.status_code == 302
