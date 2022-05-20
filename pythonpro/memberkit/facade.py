from builtins import Exception
from datetime import timedelta
from typing import List

from django.utils import timezone

from pythonpro.memberkit import api
from pythonpro.memberkit.models import SubscriptionType, Subscription, _ETERNAL_IN_HUMAM_LIFE_DAYS


def synchronize_subscription_types() -> List[SubscriptionType]:
    return [
        SubscriptionType.objects.update_or_create(
            id=dct['id'],
            defaults={'name': dct['name']}
        )[0]
        for dct in api.list_membership_levels()
    ]


def create_new_subscription_without_payment(
    user, days_of_access=_ETERNAL_IN_HUMAM_LIFE_DAYS, subscription_types=[],
    observation: str = ''
) -> Subscription:

    subscription = Subscription.objects.create(
        status=Subscription.Status.INACTIVE,
        subscriber=user,
        observation=observation,
        days_of_access=days_of_access,
    )
    subscription.subscription_types.set(subscription_types)
    return subscription


def create_new_subscription(payment, observation: str = '') -> Subscription:
    subscription_types = [item.subscription_type_relation.subscription_type for item in payment.items.all()]
    if len(subscription_types) == 0:
        raise ValueError(f"Payment {payment} doesn't have subscription types")

    # For now subscriptions has only one subscription type, so it's assumed to take
    # days of access from the first one
    days_of_access = subscription_types[0].days_of_access

    subscription = Subscription.objects.create(
        status=Subscription.Status.INACTIVE,
        payment=payment,
        subscriber=payment.user,
        observation=observation,
        days_of_access=days_of_access
    )
    subscription.subscription_types.set(subscription_types)
    return subscription


def activate(subscription, responsible=None, observation=''):
    user = subscription.subscriber
    subscription.activated_at = timezone.now()
    for subscription_type in subscription.subscription_types.all():
        expires_at = subscription.activated_at + timedelta(days=subscription_type.days_of_access)
        response_json = api.activate_user(
            user.get_full_name(), user.email, subscription_type.id, expires_at
        )
    subscription.memberkit_user_id = response_json['id']
    subscription.status = Subscription.Status.ACTIVE
    if subscription.observation:
        subscription.observation += f'\n\n {observation}'
    else:
        subscription.observation = observation
    if responsible:
        subscription.responsible = responsible
    subscription.save()
    return subscription


def inactivate(subscription, responsible=None, observation=''):
    for subscription_type in subscription.subscription_types.all().only('id'):
        api.inactivate_user(subscription.memberkit_user_id, subscription_type.id)
    subscription.status = Subscription.Status.INACTIVE
    subscription.activated_at = None
    if responsible is not None:
        subscription.responsible = responsible
    if subscription.observation:
        subscription.observation += f'\n\n {observation}'
    else:
        subscription.observation = observation
    subscription.save(update_fields=[
        'status', 'activated_at', 'responsible', 'observation'
    ])
    return subscription


class InactiveUserException(Exception):
    pass


def has_memberkit_account(user):
    return Subscription.objects.filter(
        subscriber=user, status=Subscription.Status.ACTIVE
    ).exclude(activated_at__isnull=True).exists()


def has_any_subscription(user):
    return Subscription.objects.filter(subscriber=user).exists()


def create_login_url(user):
    subscription = Subscription.objects.filter(
        subscriber=user, status=Subscription.Status.ACTIVE
    ).exclude(activated_at__isnull=True).only('memberkit_user_id').first()
    if not subscription:
        raise InactiveUserException(str(user))
    token = api.generate_token(subscription.memberkit_user_id)
    return f'https://plataforma.dev.pro.br?token={token}'


def migrate_when_status_active(user):
    status_active_but_not_activated = Subscription.objects.filter(
        subscriber=user, status=Subscription.Status.ACTIVE
    ).exclude(activated_at__isnull=False)
    for subscription in status_active_but_not_activated:
        activate(subscription, observation='Migrado automaticamente da plataforma antiga para nova')
