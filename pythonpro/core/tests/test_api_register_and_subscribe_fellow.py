import json

import pytest
from django.urls import reverse
from model_bakery import baker

from pythonpro.core.models import User
from pythonpro.memberkit.models import Subscription


def test_should_not_allow_get_calls(client):
    resp = client.get(reverse('core:api_register_and_subscribe_fellow'))
    assert 405 == resp.status_code


def test_should_not_allow_requests_without_key(client):
    resp = client.post(reverse('core:api_register_and_subscribe_fellow'))
    assert 403 == resp.status_code


def test_should_not_allow_requests_with_wrong_key(client):
    resp = client.post(reverse('core:api_register_and_subscribe_fellow'), data={'key': 'wrong'})
    assert 403 == resp.status_code


@pytest.fixture
def create_or_update_lead_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.create_or_update_lead.delay')


@pytest.fixture
def create_or_update_fellow_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.create_or_update_fellow.delay')


@pytest.fixture
def sync_user_delay_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain.sync_user_on_discourse.delay')


@pytest.fixture
def activate_mocked(mocker):
    return mocker.patch('pythonpro.core.views.activate')


@pytest.fixture
def resp(
    client, settings, create_or_update_lead_mock, create_or_update_fellow_mock, sync_user_delay_mock,
    activate_mocked
):
    baker.make("SubscriptionType", id=1)

    settings.LOCAL_API_KEY = 'correct'
    resp = client.post(
        reverse('core:api_register_and_subscribe_fellow') + '?key=correct',
        json.dumps({
            'first_name': 'Nome',
            'email': 'teste@teste.com',
            'subscription_types': [1],
            'source': 'test',
        }),
        content_type="application/json"
    )

    return resp


def test_should_allow_requests_with_correct_key_and_parameters(resp):
    assert 200 == resp.status_code


def test_should_called_create_or_update_lead(resp, create_or_update_lead_mock):
    assert create_or_update_lead_mock.callec


def test_should_called_create_or_update_fellow(resp, create_or_update_fellow_mock):
    assert create_or_update_fellow_mock.callec


def test_should_called_sync_user_delay(resp, sync_user_delay_mock):
    assert sync_user_delay_mock.callec


def test_should_create_user(resp):
    assert User.objects.get(email='teste@teste.com')


def test_should_create_subscriber(resp):
    assert Subscription.objects.get(subscriber__email='teste@teste.com')


def test_should_subscriber_has_correct_type(resp):
    subscriber = Subscription.objects.get(subscriber__email='teste@teste.com')
    assert subscriber.subscription_types.get(id=1)


def test_should_subscriber_has_been_activated(resp, activate_mocked):
    assert activate_mocked.called
