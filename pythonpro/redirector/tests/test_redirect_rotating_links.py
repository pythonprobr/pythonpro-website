import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.redirector.models import Redirect, RedirectLink
from pythonpro.redirector.facade import get_redirect_url


@pytest.fixture
def redirect(db):
    redirect = mommy.make(Redirect)
    mommy.make(RedirectLink, redirect=redirect)
    mommy.make(RedirectLink, redirect=redirect)
    return redirect


def test_should_get_url_and_increment_access_count(redirect):
    url = get_redirect_url(redirect)
    assert RedirectLink.objects.get(url=url, redirect=redirect).total_access == 1


def test_should_bring_always_link_with_less_access(redirect):
    link1 = redirect.links.first()
    link2 = redirect.links.last()

    link1.total_access = 2
    link1.save()

    assert get_redirect_url(redirect) == link2.url
    assert get_redirect_url(redirect) == link2.url


def test_should_bring_older_link_when_access_is_even(redirect):
    assert get_redirect_url(redirect) == redirect.links.first().url


@pytest.fixture
def resp1(client, redirect):
    return client.get(reverse('redirector:redirect', kwargs={'slug': redirect.slug}), secure=True)


@pytest.fixture
def resp2(client, redirect):
    return client.get(reverse('redirector:redirect', kwargs={'slug': redirect.slug}), secure=True)


def test_should_rotate_beetween_links(resp1, resp2):
    assert resp1['Location'] != resp2['Location']
