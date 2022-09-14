import pytest
from django.utils import timezone
from model_bakery import baker

from pythonpro.memberkit import facade
from pythonpro.memberkit.models import Subscription


@pytest.mark.freeze_time('2023-03-22')
def test_process_valid_subscriptions(django_user_model):
    active_user = baker.make(django_user_model)
    now = timezone.now()
    subscription = baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=active_user,
        activated_at=now,
        days_of_access=1
    )
    facade.process_expired_subscriptions(active_user.id)
    subscription.refresh_from_db()
    assert subscription.status == Subscription.Status.ACTIVE

# @pytest.mark.freeze_time('2023-03-22')
# def test_process_expired_subscriptions(django_user_model):
#     active_user = baker.make(django_user_model)
#     now = timezone.now()
#     tow_days_ago = now - timedelta(days=2)
#     subscription = baker.make(
#         Subscription,
#         status=Subscription.Status.ACTIVE,
#         subscriber=active_user,
#         activated_at=tow_days_ago,
#         days_of_access=1
#     )
#     facade.process_expired_subscriptions(active_user.id)
#     subscription.refresh_from_db()
#     assert subscription.status == Subscription.Status.INACTIVE
