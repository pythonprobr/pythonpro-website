from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.utils import timezone
from model_bakery import baker
from requests import HTTPError

from pythonpro.memberkit import facade
from pythonpro.memberkit.models import Subscription, SubscriptionType


@pytest.mark.freeze_time('2023-03-22')
def test_process_only_valid_subscriptions_success(django_user_model, mocker):
    update_mock = mocker.patch('pythonpro.memberkit.facade.api.update_user_subscription', spec=True)
    active_user = baker.make(django_user_model)
    subscription_type = baker.make(SubscriptionType)
    now = timezone.now()
    memberkit_user_id = 3
    subscription = baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=active_user,
        activated_at=now,
        days_of_access=1,
        memberkit_user_id=memberkit_user_id,
        subscription_types=[subscription_type]
    )
    facade.process_expired_subscriptions(active_user.id)
    subscription.refresh_from_db()
    tomorrow = (now + timedelta(1)).date()
    update_mock.assert_called_once_with(memberkit_user_id, subscription_type.id, 'active', tomorrow)
    assert subscription.status == Subscription.Status.ACTIVE


@pytest.mark.freeze_time('2023-03-22')
def test_process_only_expired_subscriptions(django_user_model, mocker):
    delete_mock = mocker.patch('pythonpro.memberkit.facade.api.delete_user', spec=True)
    active_user = baker.make(django_user_model)
    now = timezone.now()
    two_days_ago = now - timedelta(days=2)
    memberkit_user_id = 3
    subscription = baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=active_user,
        activated_at=two_days_ago,
        days_of_access=1,
        memberkit_user_id=memberkit_user_id
    )

    facade.process_expired_subscriptions(active_user.id)
    delete_mock.assert_called_once_with(memberkit_user_id)
    subscription.refresh_from_db()
    assert subscription.status == Subscription.Status.INACTIVE


@pytest.mark.freeze_time('2023-03-22')
def test_process_only_inactivation_of_expired_subscriptions_user_not_found(django_user_model, mocker):
    delete_mock = mocker.patch('pythonpro.memberkit.facade.api.delete_user', spec=True)

    def raise_user_not_found(memberkit_user_id):
        response = Mock()
        response.status_code = 404
        raise HTTPError(response=response)

    delete_mock.side_effect = raise_user_not_found
    active_user = baker.make(django_user_model)
    now = timezone.now()
    two_days_ago = now - timedelta(days=2)
    memberkit_user_id = 3
    subscription = baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=active_user,
        activated_at=two_days_ago,
        days_of_access=1,
        memberkit_user_id=memberkit_user_id
    )

    facade.process_expired_subscriptions(active_user.id)
    delete_mock.assert_called_once_with(memberkit_user_id)
    subscription.refresh_from_db()
    assert subscription.status == Subscription.Status.INACTIVE


@pytest.mark.freeze_time('2023-03-22')
def test_process_only_no_inactivation_of_expired_subscriptions_api_error(django_user_model, mocker):
    delete_mock = mocker.patch('pythonpro.memberkit.facade.api.delete_user', spec=True)

    def raise_user_not_found(memberkit_user_id):
        response = Mock()
        response.status_code = 500
        raise HTTPError(response=response)

    delete_mock.side_effect = raise_user_not_found
    active_user = baker.make(django_user_model)
    now = timezone.now()
    two_days_ago = now - timedelta(days=2)
    memberkit_user_id = 3
    subscription = baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=active_user,
        activated_at=two_days_ago,
        days_of_access=1,
        memberkit_user_id=memberkit_user_id
    )
    with pytest.raises(HTTPError):
        facade.process_expired_subscriptions(active_user.id)

    delete_mock.assert_called_once_with(memberkit_user_id)
    subscription.refresh_from_db()
    assert subscription.status == Subscription.Status.ACTIVE


@pytest.mark.freeze_time('2023-03-22')
def test_process_with_valid_and_expired_subscriptions_success(django_user_model, mocker):
    # Active setup
    update_mock = mocker.patch('pythonpro.memberkit.facade.api.update_user_subscription', spec=True)
    active_user = baker.make(django_user_model)
    active_subscription_type = baker.make(SubscriptionType)
    now = timezone.now()
    memberkit_user_id = 3
    active_subscription = baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=active_user,
        activated_at=now,
        days_of_access=1,
        memberkit_user_id=memberkit_user_id,
        subscription_types=[active_subscription_type]
    )

    # Expired setup
    inactivate_mock = mocker.patch('pythonpro.memberkit.facade.api.inactivate_user', spec=True)
    two_days_ago = now - timedelta(days=2)
    inactive_subscription_type = baker.make(SubscriptionType)
    to_be_inactive_subscription = baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=active_user,
        activated_at=two_days_ago,
        days_of_access=1,
        memberkit_user_id=memberkit_user_id,
        subscription_types=[inactive_subscription_type]
    )

    facade.process_expired_subscriptions(active_user.id)
    inactivate_mock.assert_called_once_with(memberkit_user_id, inactive_subscription_type.id)
    to_be_inactive_subscription.refresh_from_db()
    assert to_be_inactive_subscription.status == Subscription.Status.INACTIVE

    active_subscription.refresh_from_db()
    tomorrow = (now + timedelta(1)).date()
    update_mock.assert_called_once_with(memberkit_user_id, active_subscription_type.id, 'active', tomorrow)
    assert active_subscription.status == Subscription.Status.ACTIVE
