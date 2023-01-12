from json.decoder import JSONDecodeError
from logging import Logger

import requests as requests
from celery import shared_task
from django.conf import settings
from django_pagarme import facade as pagarme_facade
from django_pagarme.models import PagarmePayment

from pythonpro.cohorts import facade as cohort_facade
from pythonpro.discourse import facade as discourse_facade
from pythonpro.discourse.facade import MissingDiscourseAPICredentials
from pythonpro.domain.user_domain import sync_user_on_discourse
from pythonpro.email_marketing import facade as email_marketing_facade
from pythonpro.memberkit import facade as memberkit_facade
from pythonpro.memberkit.models import Subscription, SubscriptionType

_logger = Logger(__file__)
run_until_available = shared_task(autoretry_for=(JSONDecodeError,), retry_backoff=True, max_retries=None)


def validate_has_discourse_api_configuration():
    can_make_api_call = bool(settings.DISCOURSE_API_KEY and settings.DISCOURSE_API_USER)
    can_work_without_sync = not (settings.DISCOURSE_BASE_URL or can_make_api_call)
    if can_work_without_sync:
        _logger.info('Discourse Integration not available')
        return
    elif not can_make_api_call:
        raise MissingDiscourseAPICredentials('Must define both DISCOURSE_API_KEY and DISCOURSE_API_USER configs')


def remove_from_discourse(subscription: Subscription):
    """
    Synchronize user data on forum if API is configured
    :param subscription
    :return: returns result of hitting Discourse api
    """
    can_make_api_call = bool(settings.DISCOURSE_API_KEY and settings.DISCOURSE_API_USER)
    can_work_without_sync = not (settings.DISCOURSE_BASE_URL or can_make_api_call)
    if can_work_without_sync:
        _logger.info('Discourse Integration not available')
        return
    elif not can_make_api_call:
        raise MissingDiscourseAPICredentials('Must define both DISCOURSE_API_KEY and DISCOURSE_API_USER configs')

    # https://meta.discourse.org/t/sync-sso-user-data-with-the-sync-sso-route/84398
    subscriber = subscription.subscriber
    params = {
        'email': subscriber.email,
        'external_id': subscriber.id,
        'require_activation': 'false',
        'remove_groups': ','.join(subscription.discourse_groups)
    }
    sso_payload, signature = discourse_facade.generate_sso_payload_and_signature(params)
    # query_string = parse.urlencode()
    url = f'{settings.DISCOURSE_BASE_URL}/admin/users/sync_sso'
    headers = {
        'content-type': 'multipart/form-data',
        'Api-Key': settings.DISCOURSE_API_KEY,
        'Api-Username': settings.DISCOURSE_API_USER,
    }

    requests.post(url, data={'sso': sso_payload, 'sig': signature}, headers=headers)


def remove_user_from_discourse(subscription: Subscription):
    """
    Synchronize user data on forum if API is configured
    :param user_or_id: Django user or his id
    :return: returns result of hitting Discourse api
    """
    can_make_api_call = bool(settings.DISCOURSE_API_KEY and settings.DISCOURSE_API_USER)
    can_work_without_sync = not (settings.DISCOURSE_BASE_URL or can_make_api_call)
    if can_work_without_sync:
        _logger.info('Discourse Integration not available')
        return
    elif not can_make_api_call:
        raise MissingDiscourseAPICredentials('Must define both DISCOURSE_API_KEY and DISCOURSE_API_USER configs')

    # https://meta.discourse.org/t/sync-sso-user-data-with-the-sync-sso-route/84398
    subscriber = subscription.subscriber
    params = {
        'email': subscriber.email,
        'external_id': subscriber.id,
        'require_activation': 'false',
        'remove_groups': ','.join(subscription.discourse_groups)
    }
    sso_payload, signature = discourse_facade.generate_sso_payload_and_signature(params)
    # query_string = parse.urlencode()
    url = f'{settings.DISCOURSE_BASE_URL}/admin/users/sync_sso'
    headers = {
        'content-type': 'multipart/form-data',
        'Api-Key': settings.DISCOURSE_API_KEY,
        'Api-Username': settings.DISCOURSE_API_USER,
    }

    requests.post(url, data={'sso': sso_payload, 'sig': signature}, headers=headers)


def create_subscription_and_activate_services(payment: PagarmePayment) -> Subscription:
    subscription = memberkit_facade.create_new_subscription(payment, 'Criação como resposta de pagamento no Pagarme')
    phone = None
    try:
        phone = pagarme_facade.get_user_payment_profile(subscription.subscriber).phone
    except pagarme_facade.UserPaymentProfileDoesNotExist:
        phone = None
    if phone:
        phone = str(phone)
    return activate_subscription_on_all_services(
        subscription,
        observation='Ativados serviços no Memberkit, Discourse e Active Campaign',
        phone=phone
    )


def activate_subscription_on_all_services(subscription: Subscription, responsible=None, observation='',
                                          phone=None) -> Subscription:
    """
    Create or activate user account on Memberkit, Active Campaign and Discourse
    :param subscription:
    :return:
    """
    memberkit_facade.activate(subscription, responsible, observation)
    sync_all_subscriptions_on_discourse(subscription.subscriber)
    subscriber = subscription.subscriber
    tags = list(subscription.email_marketing_tags)
    if subscription.include_on_cohort:
        cohort_facade.subscribe_to_last_cohort(subscriber)
        cohort = cohort_facade.find_most_recent_cohort()
        tags.append(f'turma-{cohort.slug}')
    email_marketing_facade.create_or_update_user.delay(
        subscriber.get_full_name(),
        subscriber.email,
        None,
        *tags,
        id=subscriber.id,
        phone=phone
    )
    return subscription


def inactivate_subscription_on_all_services(subscription: Subscription, responsible=None,
                                            observation='') -> Subscription:
    """
    Inactivate user account on Memberkit, Active Campaign and Discourse
    :param subscription:
    :return:
    """
    remove_user_from_discourse(subscription)
    memberkit_facade.inactivate(subscription, responsible, observation)
    subscriber = subscription.subscriber
    tags = list(subscription.email_marketing_tags)
    email_marketing_facade.remove_tags.delay(
        subscriber.email,
        subscriber.id,
        *tags
    )
    return subscription


def inactivate_payment_subscription(payment: PagarmePayment):
    inactivate_subscription_on_all_services(payment.subscription)


def sync_all_subscriptions_on_discourse(user_id: int):
    qs = SubscriptionType.objects.filter(
        subscriptions__subscriber_id=user_id,
        subscriptions__status=Subscription.Status.ACTIVE
    ).values('discourse_groups')
    discourse_groups_in_lists = (subscription_type['discourse_groups'] for subscription_type in qs)
    discourse_groups = (group for lst in discourse_groups_in_lists for group in lst)
    sync_user_on_discourse(user_id, *discourse_groups)


def sync_user_on_all_services(user_id: int):
    sync_all_subscriptions_on_discourse(user_id)
