from model_bakery import baker

from pythonpro.domain import subscription_domain
from pythonpro.memberkit.models import SubscriptionType, Subscription


def test_user_discourse_sync_with_active_subscription(django_user_model, mocker):
    user = baker.make(django_user_model)
    fellow_subscription_type = baker.make(SubscriptionType, discourse_groups=['fellow', 'member'])
    baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscription_types=[fellow_subscription_type],
        subscriber=user
    )

    sync_user_spy = mocker.spy(subscription_domain, 'sync_user_on_discourse')
    subscription_domain.sync_all_subscriptions_on_discourse(user.id)
    assert sync_user_spy.call_count == 1
    user_id, *groups = sync_user_spy.call_args_list[0].args
    assert user_id == user.id
    assert ['fellow', 'member'] == sorted(groups)


def test_user_discourse_sync_with_active_multiple_subscriptions(django_user_model, mocker):
    user = baker.make(django_user_model)
    fellow_subscription_type = baker.make(SubscriptionType, discourse_groups=['fellow', 'lead'])
    member_subscription_type = baker.make(SubscriptionType, discourse_groups=['member'])
    baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscription_types=[fellow_subscription_type, member_subscription_type],
        subscriber=user
    )

    sync_user_spy = mocker.spy(subscription_domain, 'sync_user_on_discourse')
    subscription_domain.sync_all_subscriptions_on_discourse(user.id)
    assert sync_user_spy.call_count == 1
    user_id, *groups = sync_user_spy.call_args_list[0].args
    assert user_id == user.id
    assert ['fellow', 'lead', 'member'] == sorted(groups)
