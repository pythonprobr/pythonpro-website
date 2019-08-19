"""
Module working as a facade to all business rules from the entire system.
It must interact only with app's internal facades and can be used by views, CLI and other interfaces
"""
from django.conf import settings as _settings
from django.core.mail import send_mail as _send_mail
from mailchimp3.mailchimpclient import MailChimpError as _MailChimpError

from pythonpro.core import facade as _core_facade
from pythonpro.core.models import User as _User
from pythonpro.mailchimp import facade as _mailchimp_facade
from pythonpro.payments import facade as _payments_facade

UserCreationException = _core_facade.UserCreationException  # exposing exception on Facade


def register_lead(first_name: str, email: str, source: str = 'unknown') -> _User:
    """
    Create a new user on the system generation a random password.
    An Welcome email is sent to the user informing his password with the link to change it.
    User is also registered on Mailchimp and subscribed to LeadWorkflow and is not registered on system in case api call
    fails

    Check force_register_lead if Maichimp validation is not mandatory
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
    """
    if not source:
        source = 'unknown'
    form = _core_facade.validate_user(first_name, email, source)
    try:
        _mailchimp_facade.create_or_update_lead(first_name, email)
    except _MailChimpError:
        form.add_error('email', 'Email Inválido')
        raise UserCreationException(form)
    return _core_facade.register_lead(first_name, email, source)


def force_register_lead(first_name: str, email: str, source: str = 'unknown') -> _User:
    """
    Create a new user on the system generation a random password.
    An Welcome email is sent to the user informing his password with the link to change it.
    User is also registered on Mailchimp. But she will be registeres even if api call fails
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
    """
    user = _core_facade.register_lead(first_name, email, source)
    try:
        _mailchimp_facade.create_or_update_lead(first_name, email)
    except _MailChimpError:
        pass
    return user


def force_register_client(first_name: str, email: str, source: str = 'unknown') -> _User:
    """
    Create a new user on the system generation a random password or update existing one based on email.
    An Welcome email is sent to the user informing his password with the link to change it.
    User is also registered on Mailchimp. But she will be registered even if api call fails
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
    """
    user = _core_facade.register_client(first_name, email, source)
    try:
        _mailchimp_facade.create_or_update_client(first_name, email)
    except _MailChimpError:
        pass
    return user


def promote_client(user: _User, email_msg: str, source: str) -> None:
    """
    Promote a user to Client role and change it's role on Mailchimp. Will not fail in case API call fails.
    Email welcome email is sent to user
    :param source: source of traffic
    :param email_msg:
    :param user:
    :return:
    """
    _core_facade.promote_to_client(user, source)
    try:
        _mailchimp_facade.create_or_update_client(user.first_name, user.email)
    except _MailChimpError:
        pass
    _send_mail(
        'Inscrição no curso Pytools realizada! Confira o link com detalhes.',
        email_msg,
        _settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )


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


def run_pytools_promotion_campaign() -> int:
    """
    Run pytools campaign for users registered 7 weeks ago
    :return: number of user's marked for promotion
    """
    begin, end = _payments_facade.calculate_7th_week_before_promotion()
    promotion_users = _core_facade.find_leads_by_date_joined_interval(begin, end)
    for user in promotion_users:
        try:
            _mailchimp_facade.tag_as(user.email, 'pytools-promotion')
        except _MailChimpError:
            pass
    return len(promotion_users)


def visit_client_landing_page(user: _User, source: str) -> None:
    """
    Marke user as visited client landing page
    :param source: string containing source of traffic
    :param user:
    :return:
    """
    _core_facade.visit_client_landing_page(user, source)
    _mailchimp_facade.tag_as(user.email, 'potential-client')


def visit_member_landing_page(user, source):
    """
    Marke user as visited member landing page
    :param source: string containing source of traffic
    :param user:
    :return:
    """
    _core_facade.visit_member_landing_page(user, source)
    _mailchimp_facade.tag_as(user.email, 'potential-member')


def click_client_checkout(user: _User):
    """
        Marke user as visited member landing page
        :param source: string containing source of traffic
        :param user:
        :return:
        """
    _core_facade.client_checkout(user, None)
    _mailchimp_facade.tag_as(user.email, 'client-checkout')


def client_generated_boleto(user):
    """
        Marke user as visited member landing page
        :param source: string containing source of traffic
        :param user:
        :return:
        """
    _core_facade.client_generated_boleto(user, None)


def subscribe_to_waiting_list(user: _User, source: str) -> None:
    """
    Subscribe user to waiting list
    :param user:
    :param source:
    :return:
    """
    _core_facade.subscribe_to_waiting_list(user, source)
    _mailchimp_facade.tag_as(user.email, 'lista-de-espera')


def activate_user(user: _User, source: str) -> None:
    """
    Activate user
    :param user:
    :param source:
    :return:
    """
    _core_facade.activate_user(user, source)
    _mailchimp_facade.remove_tags(user.email, 'never-watched-video')
