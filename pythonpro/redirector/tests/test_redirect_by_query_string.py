import pytest
from django.urls import reverse
from model_bakery import baker

from pythonpro.redirector.models import Redirect, RedirectLink


@pytest.fixture
def redirect(db):
    redirect = baker.make(Redirect, url='https://google.com', slug='renzo', use_javascript=False)
    baker.make(RedirectLink, redirect=redirect, url='http://python.pro.br')
    return redirect


@pytest.fixture
def resp(client, redirect):
    return client.get(reverse('redirector:redirect', kwargs={'slug': redirect.slug}), {'utm_source': 'facebook'})


def test_status_code_should_return_302(resp):
    assert resp.status_code == 302


def test_redirect_url_with_query_string(resp, redirect):
    assert resp.url == f'{redirect.links.first().url}?utm_source=facebook'
