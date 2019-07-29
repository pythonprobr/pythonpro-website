from datetime import datetime

from rolepermissions.checkers import has_role
from rolepermissions.roles import assign_role, remove_role

from pythonpro.core.forms import UserSignupForm
from pythonpro.core.models import User


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
    Create a new user on the system generation a random password.
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
    """
    try:
        user = User.objects.filter(email=email).get()
    except User.DoesNotExist:
        form = validate_user(first_name, email, source)
        user = form.save()
    assign_role(user, 'lead')
    return user


def register_client(first_name: str, email: str, source: str) -> User:
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
        form = validate_user(first_name, email, source)
        user = form.save()
    promote_to_client(user)
    return user


def promote_to_client(user: User) -> None:
    """
    Promote a lead to user. Raises exception in case user is a member
    :param user:
    """
    if has_role(user, 'member'):
        raise UserRoleException('User is already a member')
    if has_role(user, 'client'):
        raise UserRoleException('User is already a client')
    assign_role(user, 'client')
    remove_role(user, 'lead')


def find_leads_by_date_joined_interval(begin: datetime, end: datetime):
    return list(user for user in User.objects.filter(date_joined__gte=begin, date_joined__lte=end).all() if
                not has_role(user, ['client', 'member']))


def find_user_by_email(email: str):
    return User.objects.filter(email=email).get()


def find_user_by_id(id: int):
    return User.objects.filter(id=id).get()
