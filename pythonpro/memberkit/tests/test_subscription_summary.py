from model_bakery import baker

from pythonpro.memberkit.models import UserSubscriptionsSummary, Subscription


def test_user_summary_with_no_subscriptions(logged_user):
    summary = UserSubscriptionsSummary(logged_user)
    assert not summary.has_active_subscriptions()


def test_user_with_active_subscriptions(django_user_model):
    active_users = baker.make(django_user_model, 5)
    for active_user in active_users:
        baker.make(Subscription, status=Subscription.Status.ACTIVE, subscriber=active_user)

    inactive_users = baker.make(django_user_model, 5)
    for inactive_user in inactive_users:
        baker.make(Subscription, status=Subscription.Status.INACTIVE, subscriber=inactive_user)

    active_user_ids_from_db = set(UserSubscriptionsSummary.users_with_active_subscriptions().values_list('id', flat=True))
    assert active_user_ids_from_db == set(active_user.id for active_user in active_users)
