import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains, dj_assert_template_used


@pytest.fixture
def home_resp(client):
    return _resp(client)


def _resp(client):
    """Plain function to avoid _pytest.warning_types.RemovedInPytest4Warning: Fixture "resp" called directly."""
    return client.get('/')


@pytest.fixture
def home_resp_with_user(django_user_model, client: Client, settings):
    settings.DISCOURSE_BASE_URL = 'https://forum.python.pro.br/'
    user = baker.make(django_user_model)
    client.force_login(user)
    return _resp(client)


def test_home_status_code(home_resp):
    assert 200 == home_resp.status_code


def test_thanks_status_code(client):
    resp = client.get(reverse('core:thanks'))
    assert 200 == resp.status_code


def test_home_template(home_resp):
    dj_assert_template_used(home_resp, template_name='core/index.html')


def test_forum_tab_is_not_present(home_resp):
    """
    Assert Forum tab is no present when user is not logged in
    """
    dj_assert_not_contains(home_resp, f'href="{settings.DISCOURSE_BASE_URL}"')


def test_there_is_no_none_on_home_page(home_resp):
    """
    Assert there is no None field on home form
    """
    dj_assert_not_contains(home_resp, 'value="None"')


def test_redirec_to_dashboard(home_resp_with_user):
    """
    Assert User is redirected to dashboard
    """
    assert home_resp_with_user.status_code == 302
    assert home_resp_with_user.url == reverse('dashboard:home')


@pytest.fixture
def home_resp_open_subscriptions(client, mocker):
    mocker.patch('pythonpro.core.views.is_launch_open', return_value=True)
    return _resp(client)


@pytest.mark.skip('Temporary not showing subscription link')
def test_payment_link_is_present(home_resp_open_subscriptions):
    """
    Assert Payment link is present on home page when subscriptions are open
    """
    dj_assert_contains(home_resp_open_subscriptions, reverse('checkout:bootcamp_lp'))


@pytest.fixture
def home_resp_closed_subscriptions(client, mocker):
    mocker.patch('pythonpro.core.views.is_launch_open', return_value=False)
    return _resp(client)


def test_payment_link_is_not_present(home_resp_closed_subscriptions):
    """
    Assert Payment link is not present on home page when subscriptions are closed
    """
    dj_assert_not_contains(home_resp_closed_subscriptions, reverse('checkout:bootcamp_lp'))
