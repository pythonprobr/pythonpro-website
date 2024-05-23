from datetime import timedelta

from django.core import management
from django.utils.datetime_safe import datetime
from model_bakery import baker

from pythonpro.memberkit.models import Subscription


def test_clean_discord_users_command(mocker):
    mocker.patch('pythonpro.discord.facade.devpro_discord_bot_client.list_guild_members', return_value=[])
    management.call_command('clean_discord_users')


def test_warn_users_about_subscriptions(mocker, django_user_model):
    mock = mocker.patch('pythonpro.discord.facade.warn_subscription_expiration', return_value=[])
    subscriber = baker.make(django_user_model)
    expiration_date = datetime.today() + timedelta(days=29)
    baker.make(
        Subscription, status=Subscription.Status.ACTIVE,
        expired_at=expiration_date,
        subscriber=subscriber
    )
    management.call_command('warn_users_about_subscription_expiration')
    mock.delay.assert_called_once_with(subscriber.id, expiration_date.strftime('%d/%m/%Y'))


def test_dont_botter_user_with_inactive_subscriptions(mocker, django_user_model):
    mock = mocker.patch('pythonpro.discord.facade.warn_subscription_expiration', return_value=[])
    subscriber = baker.make(django_user_model)
    expiration_date = datetime.today() + timedelta(days=29)
    baker.make(
        Subscription, status=Subscription.Status.INACTIVE,
        expired_at=expiration_date,
        subscriber=subscriber
    )
    management.call_command('warn_users_about_subscription_expiration')
    assert not mock.delay.called


def test_dont_botter_user_with_more_than_30_days_subscription(mocker, django_user_model):
    mock = mocker.patch('pythonpro.discord.facade.warn_subscription_expiration', return_value=[])
    subscriber = baker.make(django_user_model)
    expiration_date = datetime.today() + timedelta(days=31)
    baker.make(
        Subscription, status=Subscription.Status.ACTIVE,
        expired_at=expiration_date,
        subscriber=subscriber
    )
    management.call_command('warn_users_about_subscription_expiration')
    assert not mock.delay.called
