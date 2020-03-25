from datetime import datetime

import pytest
from django.urls import reverse

from pythonpro.django_assertions import (dj_assert_contains,
                                         dj_assert_not_contains)


@pytest.fixture
def resp(client):
    return client.get(reverse('checkout:pytools_oto_lp'), secure=True)


def test_redirect_user_not_logged(resp):
    assert resp.status_code == 302
    assert resp.url == reverse('checkout:pytools_lp')


def test_tag_not_called(resp, tag_as_mock):
    assert tag_as_mock.call_count == 0


@pytest.fixture
def resp_debug(client):
    return client.get(reverse('checkout:pytools_oto_lp')+'?debug=true', secure=True)


def test_page_access_with_debug_parameter(resp_debug):
    assert resp_debug.status_code == 200


def test_should_show_price_and_ctas_on_debug(resp_debug):
    dj_assert_contains(resp_debug, '<button')
    dj_assert_contains(resp_debug, '<!-- block price appearing -->')


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as.delay')


@pytest.fixture
def resp_with_lead(client_with_lead, tag_as_mock, logged_user):
    return client_with_lead.get(reverse('checkout:pytools_oto_lp'), secure=True)


def test_logged_user_status_code(resp_with_lead):
    assert resp_with_lead.status_code == 200


def test_should_run_with_countdown_time(resp_with_lead):
    assert isinstance(resp_with_lead.context['countdown_limit'], datetime)


@pytest.fixture
def resp_in_oto_season(mocker, client_with_lead, tag_as_mock):
    mocker.patch('pythonpro.checkout.views.payment_facade.is_on_pytools_oto_season', return_value=True)
    yield client_with_lead.get(reverse('checkout:pytools_oto_lp'), secure=True)


def test_should_show_price_and_ctas(resp_in_oto_season):
    dj_assert_contains(resp_in_oto_season, '<button class="cta btn btn-warning initiate-checkout')
    dj_assert_contains(resp_in_oto_season, '<!-- block price appearing -->')


@pytest.fixture
def resp_with_countdown_expired(mocker, client_with_lead, tag_as_mock):
    mocker.patch('pythonpro.checkout.views.payment_facade.is_on_pytools_oto_season', return_value=False)
    yield client_with_lead.get(reverse('checkout:pytools_oto_lp'), secure=True)


def test_should_not_show_price_and_ctas(resp_with_countdown_expired):
    dj_assert_not_contains(resp_with_countdown_expired, '<!-- block price appearing -->')
    dj_assert_not_contains(resp_with_countdown_expired, '<button class="cta btn btn-warning initiate-checkout')
