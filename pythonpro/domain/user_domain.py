"""
Module working as a facade to all business rules from the entire system.
It must interact only with app's internal facades and can be used by views, CLI and other interfaces
"""
from logging import Logger

import requests
from celery import shared_task
from django.conf import settings

from pythonpro.cohorts import facade as _cohorts_facade
from pythonpro.core import facade as _core_facade
from pythonpro.core.models import User as _User
from pythonpro.discourse.facade import MissingDiscourseAPICredentials, generate_sso_payload_and_signature
from pythonpro.email_marketing import facade as _email_marketing_facade
from pythonpro.domain.subscription_domain import subscribe_with_no_role

_logger = Logger(__file__)

UserCreationException = _core_facade.UserCreationException  # exposing exception on Facade

__all__ = [
    'register_lead', 'activate_user', 'find_user_interactions',
    'visit_member_landing_page', 'promote_member', 'promote_bootcamper', 'promote_webdev', 'promote_data_scientist',
    'find_user_by_email', 'find_user_by_id', 'force_register_lead', 'subscribe_to_waiting_list',
    'force_register_member', 'click_member_checkout', 'subscribe_anonymous_user_to_waiting_list'
]


def register_lead(first_name: str, email: str, source: str = 'unknown', tags: list = []) -> _User:
    """
    Create a new user on the system generation a random password.
    An Welcome email is sent to the user informing his password with the link to change it.
    User is also registered on Email Marketing and subscribed to LeadWorkflow and is not registered on system in case
    api call fails

    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
    """
    if not source:
        source = 'unknown'
    _core_facade.validate_user(first_name, email, source)
    lead = _core_facade.register_lead(first_name, email, source)
    _email_marketing_facade.create_or_update_lead.delay(first_name, email, *tags, id=lead.id)

    return lead


def force_register_lead(first_name: str, email: str, source: str = 'unknown') -> _User:
    """
    Create a new user on the system generation a random password.
    An Welcome email is sent to the user informing his password with the link to change it.
    User is also registered on Email Marketing. But she will be registered even if api call fails
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
    """
    user = _core_facade.register_lead(first_name, email, source)
    _email_marketing_facade.create_or_update_lead.delay(first_name, email, id=user.id)
    return user


def force_register_member(first_name, email, source='unknown'):
    """
    Create a new user on the system generation a random password or update existing one based on email.
    An Welcome email is sent to the user informing his password with the link to change it.
    User is also registered on Email Marketing. But she will be registered even if api call fails
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
    """
    user = _core_facade.register_member(first_name, email, source)
    _cohorts_facade.subscribe_to_last_cohort(user)
    cohort = _cohorts_facade.find_most_recent_cohort()
    sync_user_on_discourse.delay(user.id)
    _email_marketing_facade.create_or_update_member.delay(first_name, email, f'turma-{cohort.slug}', id=user.id)
    return user


def promote_member(user: _User, source: str) -> _User:
    """
    Promote a user to Member role and change it's role on Email Marketing. Will not fail in case API call fails.
    Email welcome email is sent to user
    :param source: source of traffic
    :param user:
    :return:
    """
    _core_facade.promote_to_member(user, source)
    _cohorts_facade.subscribe_to_last_cohort(user)
    cohort = _cohorts_facade.find_most_recent_cohort()
    sync_user_on_discourse.delay(user.id)
    _email_marketing_facade.create_or_update_member.delay(
        user.first_name, user.email, f'turma-{cohort.slug}', id=user.id
    )
    return user


def promote_bootcamper(user: _User, source: str) -> _User:
    """
    Promote a user to Bootcamper role and change it's role on Email Marketing. Will not fail in case API call fails.
    Email welcome email is sent to user
    :param source: source of traffic
    :param user:
    :return:
    """
    _core_facade.promote_to_bootcamper(user, source)
    _cohorts_facade.subscribe_to_last_cohort(user)
    cohort = _cohorts_facade.find_most_recent_cohort()
    sync_user_on_discourse.delay(user.id)
    _email_marketing_facade.create_or_update_bootcamper.delay(
        user.first_name, user.email, f'turma-{cohort.slug}', id=user.id
    )
    return user


def promote_webdev(user: _User, source: str) -> _User:
    """
    Promote a user to Webdev role and change it's role on Email Marketing. Will not fail in case API call fails.
    Email welcome email is sent to user
    :param source: source of traffic
    :param user:
    :return:
    """
    _core_facade.promote_to_webdev(user, source)
    sync_user_on_discourse.delay(user.id)
    _email_marketing_facade.create_or_update_webdev.delay(user.first_name, user.email, id=user.id)
    return user


def promote_data_scientist(user: _User, source: str) -> _User:
    """
    Promote a user to DataScientist role and change it's role on Email Marketing. Will not fail in case API call fails.
    Email welcome email is sent to user
    :param source: source of traffic
    :param user:
    :return:
    """
    _core_facade.promote_to_data_scientist(user, source)
    sync_user_on_discourse.delay(user.id)
    _email_marketing_facade.create_or_update_data_scientist.delay(
        user.first_name, user.email, id=user.id)
    return user


def promote_pythonista(user: _User, source: str) -> _User:
    """
    Promote a user to Pythonista role and change it's role on Email Marketing. Will not fail in case API call fails.
    Email welcome email is sent to user
    :param source: source of traffic
    :param user:
    :return:
    """
    _core_facade.promote_to_pythonista(user, source)
    sync_user_on_discourse.delay(user.id)
    _email_marketing_facade.create_or_update_pythonista.delay(
        user.first_name, user.email, id=user.id)
    return user


def find_user_by_email(user_email: str) -> _User:
    """
    Find user by her email
    :param user_email:
    :return: User
    """
    return _core_facade.find_user_by_email(user_email)


def find_user_by_id(user_id: int) -> _User:
    """
    Find user by her id
    :param user_id:
    :return:
    """
    return _core_facade.find_user_by_id(user_id)


def find_user_interactions(user: _User):
    """
    Find all user interactions ordered by creation date desc
    :param user:
    :return: list of user interactions
    """
    return _core_facade.find_user_interactions(user)


def visit_member_landing_page(user, source):
    """
    Mark user as visited member landing page
    :param source: string containing source of traffic
    :param user:
    :return:
    """
    _core_facade.visit_member_landing_page(user, source)
    _email_marketing_facade.tag_as.delay(user.email, user.id, 'potential-member')


def visit_launch_landing_page(user, source):
    """
    Mark user as visited launch landing page
    :param source: string containing source of traffic
    :param user:
    :return:
    """
    _core_facade.visit_launch_landing_page(user, source)


def subscribe_launch_landing_page(user, source):
    """
    Mark user as subscribed to launch
    :param source: string containing source of traffic
    :param user:
    :return:
    """
    _core_facade.subscribe_to_launch(user, source)


def click_member_checkout(user):
    """
    Mark user as visited member landing page
    :param user:
    :return:
    """
    _core_facade.member_checkout(user, None)
    _email_marketing_facade.tag_as.delay(user.email, user.id, 'member-checkout')


def member_generated_boleto(user):
    _core_facade.member_generated_boleto(user, None)


def subscribe_to_waiting_list(session_id, user: _User, phone: str, source: str) -> None:
    """
    Subscribe user to waiting list
    :param session_id:
    :param user:
    :param phone:
    :param source:
    :return:
    """
    _core_facade.subscribe_to_waiting_list(user, source)
    subscribe_with_no_role.delay(
        session_id, user.first_name, user.email, 'lista-de-espera', id=user.id, phone=phone
    )


def subscribe_anonymous_user_to_waiting_list(session_id, email: str, name: str, phone: str, source: str) -> None:
    """
    Subscribe anonymous user to waiting list
    :param session_id:
    :param email:
    :param name:
    :param phone:
    :param source:
    :return:
    """
    try:
        user = _core_facade.find_user_by_email(email)
    except _User.DoesNotExist:
        subscribe_with_no_role.delay(session_id, name, email, 'lista-de-espera', phone=phone)
    else:
        subscribe_to_waiting_list(session_id, user, phone, source)


def activate_user(user: _User, source: str) -> None:
    """
    Activate user
    :param user:
    :param source:
    :return:
    """
    _core_facade.activate_user(user, source)
    _email_marketing_facade.remove_tags.delay(user.email, user.id, 'never-watched-video')


def visit_cpl1(user: _User, source: str) -> None:
    """
    User visit CPL1
    :param user:
    :param source:
    :return:
    """
    _core_facade.visit_cpl1(user, source)
    _email_marketing_facade.tag_as.delay(user.email, user.id, 'cpl1')


def visit_cpl2(user: _User, source: str) -> None:
    """
    User visit CPL2
    :param user:
    :param source:
    :return:
    """
    _core_facade.visit_cpl2(user, source)
    _email_marketing_facade.tag_as.delay(user.email, user.id, 'cpl2')


def visit_cpl3(user: _User, source: str) -> None:
    """
    User visit CPL2
    :param user:
    :param source:
    :return:
    """
    _core_facade.visit_cpl3(user, source)
    _email_marketing_facade.tag_as.delay(user.email, user.id, 'cpl3')


@shared_task
def sync_user_on_discourse(user_or_id):
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

    user = _core_facade.find_user_by_id(user_or_id)

    # https://meta.discourse.org/t/sync-sso-user-data-with-the-sync-sso-route/84398
    params = {
        'email': user.email,
        'external_id': user.id,
        'require_activation': 'false',
        'groups': ','.join(g.name for g in user.groups.all())
    }
    sso_payload, signature = generate_sso_payload_and_signature(params)
    # query_string = parse.urlencode()
    url = f'{settings.DISCOURSE_BASE_URL}/admin/users/sync_sso'
    headers = {
        'content-type': 'multipart/form-data',
        'Api-Key': settings.DISCOURSE_API_KEY,
        'Api-Username': settings.DISCOURSE_API_USER,
    }

    requests.post(url, data={'sso': sso_payload, 'sig': signature}, headers=headers)
