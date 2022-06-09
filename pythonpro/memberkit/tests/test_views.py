import pytest
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_template_used
from pythonpro.memberkit.models import Subscription, SubscriptionType


@pytest.fixture
def mock_generater_token(mocker):
    return mocker.patch(
        'pythonpro.memberkit.views.facade.api.generate_token',
        return_value='some_token')


@pytest.fixture
def mock_activate(mocker):
    def active_subscription(subscription, *args, **kwargs):
        subscription.activated_at = timezone.now()
        subscription.memberkit_user_id = 1
        subscription.save()

    return mocker.patch(
        'pythonpro.memberkit.views.facade.activate', side_effect=active_subscription)


def test_migrate_page_status_code(client_with_user, mock_generater_token):
    resp = client_with_user.get(reverse('migrate_to_memberkit'))
    assert resp.status_code == 200
    assert not mock_generater_token.called


def test_succesful_migration(client_with_user, logged_user, mock_activate, mock_generater_token):
    subscription_type = baker.make(SubscriptionType)
    subscription = baker.make(
        Subscription, subscriber=logged_user, status=Subscription.Status.ACTIVE, activated_at=None
    )
    subscription.subscription_types.add(subscription_type)
    resp = client_with_user.post(reverse('migrate_to_memberkit'))
    assert resp.status_code == 302
    mock_activate.assert_called_once_with(
        subscription, observation='Migrado automaticamente da plataforma antiga para nova'
    )
    assert resp.url == 'https://plataforma.dev.pro.br?token=some_token'


def test_migration_fail_for_user_without_subscriptions(client_with_user):
    resp = client_with_user.post(reverse('migrate_to_memberkit'))
    dj_assert_template_used(resp, 'memberkit/manual_migration.html')
