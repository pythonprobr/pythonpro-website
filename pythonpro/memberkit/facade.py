from builtins import Exception
from datetime import timedelta
from itertools import count
from logging import Logger
from typing import List

from celery import shared_task
from django.utils import timezone

from pythonpro.memberkit import api
from pythonpro.memberkit.models import SubscriptionType, Subscription, YEAR_IN_DAYS, UserSubscriptionsSummary

_logger = Logger(__file__)


def synchronize_subscription_types() -> List[SubscriptionType]:
    return [
        SubscriptionType.objects.update_or_create(
            id=dct['id'],
            defaults={'name': dct['name']}
        )[0]
        for dct in api.list_membership_levels()
    ]


def create_new_subscription_without_payment(
        user, days_of_access=YEAR_IN_DAYS, subscription_types=[], observation: str = ''
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


# Esses ids de comunidade são os verdadeiros de produção, que foram extraidos do memberkit
IDS_COMUNIDADE_SUBSCRIPTION = {11610, 12180}


def activate(subscription, responsible=None, observation=''):
    user = subscription.subscriber
    if subscription.status == Subscription.Status.INACTIVE or subscription.activated_at is None:
        subscription.activated_at = timezone.now()
    for subscription_type in subscription.subscription_types.all():
        expires_at = subscription.activated_at + timedelta(days=subscription_type.days_of_access)
        if subscription_type.id in IDS_COMUNIDADE_SUBSCRIPTION:
            active_comunidade_subscriptions = Subscription.objects.filter(
                subscriber_id=user.id,
                status=Subscription.Status.ACTIVE,
                subscription_types__in=IDS_COMUNIDADE_SUBSCRIPTION
            )

            max_remaining_days = max(s.remaining_days for s in active_comunidade_subscriptions)
            expires_at += timedelta(days=max_remaining_days)
            subscription.days_of_access += max_remaining_days

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


def clean_memberkit_users_up():
    total = 0
    for page in count(1):
        memberkit_users = api.list_users(page)
        if len(memberkit_users) == 0:
            break
        for memberkit_user in memberkit_users:
            total += 1
            memberkit_user_id = int(memberkit_user['id'])
            has_active_subscription = Subscription.objects.filter(memberkit_user_id=memberkit_user_id, status=Subscription.Status.ACTIVE).exists()
            if not has_active_subscription:
                api.delete_user(memberkit_user_id)
                print(f'Desativado: {memberkit_user_id} ############################################')
            else:
                print(f'Ativo: {memberkit_user_id}')
    return total


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


@shared_task
def process_expired_subscriptions(user_id):
    now = timezone.now()
    summary = UserSubscriptionsSummary(user_id)
    active_subscriptions = list(summary.active_subscriptions())
    for subscription in active_subscriptions:
        if subscription.expires_at < now:
            subscription.status = Subscription.Status.INACTIVE
            subscription.save()


def inactivate_expired_subscriptions():
    for user_id in UserSubscriptionsSummary.users_with_active_subscriptions().values_list('id', flat=True):
        _logger.info(f'Adding task to process subscriptions expiration for user_id: {user_id}')
        process_expired_subscriptions.delay(user_id)
