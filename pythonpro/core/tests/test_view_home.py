import pytest
from django.urls import reverse


@pytest.fixture
def home_resp(client):
    return _resp(client)


def _resp(client):
    """Plain function to avoid _pytest.warning_types.RemovedInPytest4Warning: Fixture "resp" called directly."""
    return client.get('/')


def test_home_status_code(home_resp):
    assert home_resp.status_code == 302
    assert home_resp.url == reverse('dashboard:home')


def test_thanks_status_code(client):
    resp = client.get(reverse('core:thanks'))
    assert 200 == resp.status_code


@pytest.fixture
def home_resp_open_subscriptions(client, mocker):
    mocker.patch('pythonpro.core.views.is_launch_open', return_value=True)
    return _resp(client)


@pytest.fixture
def home_resp_closed_subscriptions(client, mocker):
    mocker.patch('pythonpro.core.views.is_launch_open', return_value=False)
    return _resp(client)
