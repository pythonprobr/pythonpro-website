from builtins import Exception
from itertools import count
from logging import Logger
from time import sleep
from typing import List

from celery import shared_task
from django.db import transaction
from django.utils import timezone
from requests import HTTPError

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
        old_days_of_access=days_of_access,
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
        old_days_of_access=days_of_access
    )
    subscription.subscription_types.set(subscription_types)
    return subscription


# Esses ids de comunidade são os verdadeiros de produção, que foram extraidos do memberkit
IDS_COMUNIDADE_SUBSCRIPTION = {11610, 12180}


def activate(subscription, responsible=None, observation=''):
    user = subscription.subscriber
    if subscription.activated_at is None:
        # Faz extensão da anualidade se for a primeira ativação
        subscription.activated_at = timezone.now()
        for subscription_type in subscription.subscription_types.all():
            if subscription_type.id in IDS_COMUNIDADE_SUBSCRIPTION:
                active_comunidade_subscriptions = Subscription.objects.filter(
                    subscriber_id=user.id,
                    status=Subscription.Status.ACTIVE,
                    subscription_types__in=IDS_COMUNIDADE_SUBSCRIPTION
                )

                max_remaining_days = max(
                    (s.remaining_days for s in active_comunidade_subscriptions),
                    default=0
                )
                subscription.days_of_access += max_remaining_days

            response_json = api.activate_user(
                user.get_full_name(), user.email, subscription_type.id, subscription.expires_at
            )
        subscription.memberkit_user_id = response_json['id']
    else:
        # Se for a segunda, só usa os dados já calculados
        for subscription_type in subscription.subscription_types.all():
            response_json = api.activate_user(
                user.get_full_name(), user.email, subscription_type.id, subscription.expires_at
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
    if responsible is not None:
        subscription.responsible = responsible
    if subscription.observation:
        subscription.observation += f'\n\n {observation}'
    else:
        subscription.observation = observation
    subscription.save(update_fields=[
        'status', 'responsible', 'observation'
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
            has_active_subscription = Subscription.objects.filter(
                memberkit_user_id=memberkit_user_id, status=Subscription.Status.ACTIVE
            ).exists()
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
    inactive_subscriptions = [s for s in active_subscriptions if s.status == Subscription.Status.INACTIVE]
    active_subscriptions = [s for s in active_subscriptions if s.status == Subscription.Status.ACTIVE]
    if len(active_subscriptions) == 0:
        for memberkit_user_id in summary.memberkit_user_ids():
            _logger.info(f'Deleted memberkit account for user_id: {user_id}')
            try:
                api.delete_user(memberkit_user_id)
            except HTTPError as e:
                if e.response.status_code != 404:
                    raise e

        with transaction.atomic():
            for subscription in inactive_subscriptions:
                subscription.save()
    else:
        for active_subscription in active_subscriptions:
            for subscription_type_id in active_subscription.subscription_types.all().values_list('id', flat=True):
                _logger.info(f'Activated {active_subscription.name} for user_id: {user_id}')
                api.update_user_subscription(
                    active_subscription.memberkit_user_id,
                    subscription_type_id,
                    'active',
                    active_subscription.expires_at.date()
                )
        for inactive_subscription in inactive_subscriptions:
            _logger.info(f'Inactivated {inactive_subscription.name} for user_id: {user_id}')
            try:
                inactivate(inactive_subscription, observation='Inativada por data de experição7')
            except HTTPError as e:
                if e.response.status_code != 404:
                    raise e


def inactivate_expired_subscriptions():
    count = 0
    for user_id in UserSubscriptionsSummary.users_with_expired_but_active_subscriptions().values_list('id', flat=True):
        count += 1
        _logger.info(f'Adding task to process subscriptions expiration for user_id: {user_id}')
        process_expired_subscriptions.delay(user_id)
        sleep(5)
    return f'Created tasks for {count} users'
