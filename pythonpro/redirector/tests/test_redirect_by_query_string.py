import pytest
from django.urls import reverse
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_contains
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


@pytest.fixture
def resp_without_query_string(client, redirect):
    return client.get(reverse('redirector:redirect', kwargs={'slug': redirect.slug}))


def test_status_code_should_return_302_without_query_string(resp_without_query_string):
    assert resp_without_query_string.status_code == 302


def test_redirect_url_without_query_string(resp_without_query_string, redirect):
    assert resp_without_query_string.url == redirect.links.first().url


@pytest.fixture
def redirect_link_with_query_string(db):
    redirect = baker.make(Redirect, url='https://google.com', slug='renzo', use_javascript=False)
    baker.make(RedirectLink, redirect=redirect, url='http://python.pro.br?utm_source=instagram&utm_content=bio')
    return redirect


@pytest.fixture
def resp_redirect_link_with_qs(client, redirect_link_with_query_string):
    return client.get(reverse('redirector:redirect', kwargs={'slug': redirect_link_with_query_string.slug}),
                      {'utm_source': 'facebook'})


def test_status_code_should_return_302_with_query_string_in_redirect_link(resp_redirect_link_with_qs):
    assert resp_redirect_link_with_qs.status_code == 302


def test_redirect_url_with_query_string_in_redirect_link(resp_redirect_link_with_qs, redirect_link_with_query_string):
    assert resp_redirect_link_with_qs.url == f'{redirect_link_with_query_string.links.first().url}&utm_source=facebook'


@pytest.fixture
def redirect_javascript(db):
    redirect = baker.make(Redirect, url='https://google.com', slug='renzo', use_javascript=True)
    baker.make(RedirectLink, redirect=redirect, url='http://python.pro.br')
    return redirect


@pytest.fixture
def resp_javascript(client, redirect_javascript):
    return client.get(reverse('redirector:redirect', kwargs={'slug': redirect_javascript.slug}),
                      {'utm_source': 'facebook'})


def test_status_code_should_return_200(resp_javascript):
    assert resp_javascript.status_code == 200


def test_redirect_javascript_url_with_query_string(resp_javascript, redirect_javascript):
    dj_assert_contains(resp_javascript, f'{redirect_javascript.links.first().url}?utm_source=facebook')
