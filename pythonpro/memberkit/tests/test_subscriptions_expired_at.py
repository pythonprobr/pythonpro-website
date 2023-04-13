# Workaround since module beginning with number can't be imported in regular way
from datetime import timedelta
from importlib import import_module

from django.utils import timezone
from model_bakery import baker

from pythonpro.memberkit.models import Subscription

# Workaround since module beginning with number can't be imported in regular way
migration_module = import_module('pythonpro.memberkit.migrations.0013_populate_expired_at')


def test_populate_expired_at_for_subscriptions_with_activation_at(db):
    now = timezone.now()
    baker.make(Subscription, activated_at=now, old_days_of_access=1, _quantity=5)
    tomorrow = (now + timedelta(days=1)).date()
    migration_module.fill_expired_at(Subscription)
    for subscription in Subscription.objects.all():
        assert subscription.expired_at == tomorrow


def test_populate_expired_at_for_subscriptions_with_activation_at_null(db):
    number_of_subscriptions = 5
    baker.make(Subscription, activated_at=None, old_days_of_access=1, _quantity=number_of_subscriptions)
    migration_module.fill_expired_at(Subscription)
    assert Subscription.objects.filter(expired_at__isnull=True).count() == number_of_subscriptions


def test_populate_expired_at_with_null_on_reverse_migration(db):
    now = timezone.now()
    number_of_subscriptions = 5
    baker.make(Subscription, expired_at=now.date(), _quantity=number_of_subscriptions)
    migration_module.make_expired_at_null(Subscription)
    assert Subscription.objects.filter(expired_at__isnull=True).count() == number_of_subscriptions
