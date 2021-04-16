import pytest
from django.test import Client
from django.urls import reverse
from model_bakery import baker


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
    assert 302 == home_resp.status_code


def test_thanks_status_code(client):
    resp = client.get(reverse('core:thanks'))
    assert 200 == resp.status_code


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


@pytest.fixture
def home_resp_closed_subscriptions(client, mocker):
    mocker.patch('pythonpro.core.views.is_launch_open', return_value=False)
    return _resp(client)
