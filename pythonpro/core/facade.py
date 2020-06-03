from datetime import datetime
from typing import Union

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from rolepermissions.checkers import has_role
from rolepermissions.roles import assign_role, remove_role

from pythonpro import settings
from pythonpro.absolute_uri import build_absolute_uri
from pythonpro.core.forms import UserSignupForm
from pythonpro.core.models import User, UserInteraction


class UserCreationException(Exception):

    def __init__(self, form: UserSignupForm, *args: object) -> None:
        super().__init__(*args)
        self.form = form


class UserRoleException(Exception):
    pass


def validate_user(first_name: str, email: str, source: str) -> UserSignupForm:
    """
    Validate a user
    :param first_name:
    :param email:
    :param source:
    :return:
    """
    data = {'first_name': first_name, 'email': email, 'source': source}

    form = UserSignupForm(data)
    if not form.is_valid():
        raise UserCreationException(form)
    return form


def register_lead(first_name: str, email: str, source: str) -> User:
    """
    Create a new user on the system generating a random password.
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
    """
    try:
        user = User.objects.filter(email=email).get()
    except User.DoesNotExist:
        user = save_and_sent_password_email(first_name, email, source)
        UserInteraction(category=UserInteraction.BECOME_LEAD, source=source, user=user).save()
    assign_role(user, 'lead')
    return user


def save_and_sent_password_email(first_name, email, source):
    form = validate_user(first_name, email, source)
    user = form.save()
    subject = 'Confira sua senha do Python Pro'
    change_password_uri = build_absolute_uri(reverse('core:profile_password'))
    ctx = {
        'first_name': first_name,
        'password': form.plain_password,
        'change_password_uri': change_password_uri
    }
    msg = render_to_string('core/password_email.txt', context=ctx)
    send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [user.email])
    return user


def register_member(first_name, email, source):
    """
    Create a new user on the system generation a random password or update existing on based on email.
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
        """
    try:
        user = User.objects.filter(email=email).get()
    except User.DoesNotExist:
        user = save_and_sent_password_email(first_name, email, source)
    promote_to_member(user, source)
    return user


def promote_to_member(user: User, source: str) -> None:
    """
    Promote a user do member. Raises exception in case user is a member
    :param user:
    """
    if has_role(user, 'member'):
        raise UserRoleException('User is already a member')
    UserInteraction(category=UserInteraction.BECOME_MEMBER, source=source, user=user).save()
    assign_role(user, 'member')
    remove_role(user, 'lead')
    remove_role(user, 'webdev')
    remove_role(user, 'client')


def promote_to_webdev(user: User, source: str) -> None:
    """
    Promote a user do webdev. Raises exception in case user is a member
    :param user:
    """
    if has_role(user, 'member'):
        raise UserRoleException('User is already a member')
    if has_role(user, 'webdev'):
        raise UserRoleException('User is already a webdev')
    UserInteraction(category=UserInteraction.BECOME_WEBDEV, source=source, user=user).save()
    assign_role(user, 'webdev')
    remove_role(user, 'lead')
    remove_role(user, 'client')


def promote_to_data_scientist(user, source):
    UserInteraction(category=UserInteraction.BECOME_DATA_SCIENTIST, source=source, user=user).save()
    assign_role(user, 'data_scientist')


def visit_launch_landing_page(user: User, source: str):
    return UserInteraction(category=UserInteraction.LAUNCH_LP, source=source, user=user).save()


def subscribe_to_launch(user: User, source: str):
    return UserInteraction(category=UserInteraction.LAUNCH_SUBSCRIPTION, source=source, user=user).save()


def visit_cpl1(user: User, source: str):
    return UserInteraction(category=UserInteraction.CPL1, source=source, user=user).save()


def visit_cpl2(user: User, source: str):
    return UserInteraction(category=UserInteraction.CPL2, source=source, user=user).save()


def visit_cpl3(user: User, source: str):
    return UserInteraction(category=UserInteraction.CPL3, source=source, user=user).save()


def find_leads_by_date_joined_interval(begin: datetime, end: datetime):
    return list(user for user in User.objects.filter(date_joined__gte=begin, date_joined__lte=end).all() if
                not has_role(user, ['client', 'member']))


def find_user_by_email(email: str):
    return User.objects.filter(email=email).get()


def find_user_by_id(user_or_user_id: Union[int, User]):
    """
    Find user by his id. If user instance is passed he is returned without directly
    :param user_or_user_id:
    :return:
    """
    if isinstance(user_or_user_id, User):
        return user_or_user_id
    return User.objects.filter(id=user_or_user_id).get()


def find_user_interactions(user: User):
    """
    Find all user interactions ordered by creation date desc
    :param user:
    :return: list of user interactions
    """
    return list(UserInteraction.objects.filter(user=user).order_by('-creation'))


def visit_member_landing_page(user: User, source: str):
    return UserInteraction(category=UserInteraction.MEMBER_LP, source=source, user=user).save()


def activate_user(user: User, source: str):
    return UserInteraction(category=UserInteraction.ACTIVATED, source=source, user=user).save()


def member_checkout_form(user: User, source='unknown'):
    return UserInteraction(category=UserInteraction.MEMBER_CHECKOUT_FORM, source=source, user=user).save()


def webdev_checkout_form(user: User, source='unknown'):
    return UserInteraction(category=UserInteraction.WEBDEV_CHECKOUT_FORM, source=source, user=user).save()


def member_checkout(user: User, source='unknown'):
    return UserInteraction(category=UserInteraction.MEMBER_CHECKOUT, source=source, user=user).save()


def member_generated_boleto(user, source='unknow'):
    return UserInteraction(category=UserInteraction.MEMBER_BOLETO, source=source, user=user).save()


def subscribe_to_waiting_list(user: User, source: str):
    return UserInteraction(category=UserInteraction.WAITING_LIST, source=source, user=user).save()


def is_client(user: User):
    return has_role(user, 'client')


def is_lead(user: User):
    return has_role(user, 'lead')


def is_member(user: User):
    return has_role(user, 'member')


def is_webdev(user: User):
    return has_role(user, 'webdev')


def is_data_scientist(user):
    return has_role(user, 'data_scientist')
