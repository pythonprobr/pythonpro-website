from datetime import datetime

import freezegun
import pytest
import pytz
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.domain import user_facade
from pythonpro.payments import facade


@pytest.fixture
def client_lp_resp(client_with_lead, mocker, logged_user):
    tag_as = mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as')
    yield client_with_lead.get(reverse('client_landing_page'), secure=True)
    tag_as.assert_called_once_with(logged_user.email, logged_user.id, 'potential-client')


@pytest.fixture
def anonymous_client_lp_resp(client, mocker):
    tag_as = mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as')
    yield client.get(reverse('client_landing_page'), secure=True)
    assert tag_as.call_count == 0


def test_logged_status_code(client_lp_resp):
    assert client_lp_resp.status_code == 200


def test_logged_non_promotion_price(client_lp_resp):
    dj_assert_contains(client_lp_resp, facade.PYTOOLS_PRICE)


@pytest.fixture
def client_promotion_lp_resp(client_with_lead, mocker, logged_user):
    tag_as = mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as')
    logged_user.date_joined = datetime(2019, 6, 3, tzinfo=pytz.utc)
    logged_user.save()
    with freezegun.freeze_time('2019-07-22'):
        yield client_with_lead.get(reverse('client_landing_page') + '?utm_source=google', secure=True)
    tag_as.assert_called_once_with(logged_user.email, logged_user.id, 'potential-client')


def test_logged_promotion_price(client_promotion_lp_resp):
    dj_assert_contains(client_promotion_lp_resp, facade.PYTOOLS_PROMOTION_PRICE)


def test_user_visited_lp(client_promotion_lp_resp, logged_user):
    interaction = user_facade.find_user_interactions(logged_user)[0]
    assert ('CLIENT_LP', 'google') == (interaction.category, interaction.source)


def test_anonymous_access_status_code(anonymous_client_lp_resp):
    assert anonymous_client_lp_resp.status_code == 200


@pytest.fixture
def client_checkout_click_resp(client_with_lead, mocker, logged_user):
    tag_as = mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as')
    yield client_with_lead.post(reverse('payments:client_checkout'), secure=True)
    tag_as.assert_called_once_with(logged_user.email, logged_user.id, 'client-checkout')


def test_checkout_click(client_checkout_click_resp):
    assert client_checkout_click_resp.status_code == 200


def test_checkout_user_interaction(client_checkout_click_resp, logged_user):
    assert 'CLIENT_CHECKOUT' == user_facade.find_user_interactions(logged_user)[0].category
