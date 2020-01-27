from datetime import datetime

import pytest

from django.urls import reverse
from pythonpro.payments.facade import PYTOOLS_OTO_PRICE


def test_should_redirect_to_normal_client_landing_page_when_user_is_not_logged(client):
    resp = client.get(reverse('payments:client_landing_page_oto'), secure=True)
    assert resp.status_code == 302


def test_should_not_redirect_when_debug_is_setted(client):
    resp = client.get(reverse('payments:client_landing_page_oto') + "?debug=1", secure=True)
    assert resp.status_code == 200


@pytest.fixture
def resp_with_lead(client_with_lead):
    yield client_with_lead.get(reverse('payments:client_landing_page_oto'), secure=True)


def test_should_run_ok_to_logged_lead(resp_with_lead):
    assert resp_with_lead.status_code == 200


def test_should_run_with_oto_price(resp_with_lead):
    assert resp_with_lead.context['price'] == PYTOOLS_OTO_PRICE


def test_should_run_with_countdown_time(resp_with_lead):
    assert isinstance(resp_with_lead.context['countdown_limit'], datetime)
