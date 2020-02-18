from datetime import datetime

import pytest

from django.urls import reverse
from django.utils import timezone

from pythonpro.django_assertions import dj_assert_not_contains, dj_assert_contains
from pythonpro.payments.facade import PYTOOLS_DO_PRICE


def test_should_show_login_form_when_user_is_not_logged(client):
    resp = client.get(reverse('payments:client_landing_page_do'), secure=True)
    dj_assert_contains(resp, 'login')


def test_should_not_redirect_when_debug_is_setted(client):
    resp = client.get(reverse('payments:client_landing_page_do') + "?debug=1", secure=True)
    assert resp.status_code == 200


@pytest.fixture
def resp_with_lead(client_with_lead):
    yield client_with_lead.get(reverse('payments:client_landing_page_do'), secure=True)


def test_should_run_ok_to_logged_lead(resp_with_lead):
    assert resp_with_lead.status_code == 200


def test_should_not_show_login_form_when_user_is_logged(resp_with_lead):
    dj_assert_not_contains(resp_with_lead, 'login')


def test_should_run_with_do_price(resp_with_lead):
    assert resp_with_lead.context['price'] == PYTOOLS_DO_PRICE


def test_should_run_with_countdown_time(resp_with_lead):
    assert isinstance(resp_with_lead.context['countdown_limit'], datetime)


def test_should_show_price_and_ctas(resp_with_lead):
    dj_assert_contains(resp_with_lead, '<!-- block price appearing -->')
    dj_assert_contains(resp_with_lead, '<button')


@pytest.fixture
def resp_with_countdown_expired(client_with_lead):
    session = client_with_lead.session
    session['DO_countdown_limit'] = timezone.now().strftime('%Y-%m-%d-%H-%M-%S')
    session.save()

    yield client_with_lead.get(reverse('payments:client_landing_page_do'), secure=True)


def test_should_not_show_price_and_ctas(resp_with_countdown_expired):
    dj_assert_not_contains(resp_with_countdown_expired, '<!-- block price appearing -->')
    dj_assert_not_contains(resp_with_countdown_expired, '<button')
