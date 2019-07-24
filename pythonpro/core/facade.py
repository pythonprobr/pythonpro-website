from rolepermissions.roles import assign_role

from pythonpro.core.forms import UserSignupForm
from pythonpro.core.models import User


class UserCreationException(Exception):

    def __init__(self, form: UserSignupForm, *args: object) -> None:
        super().__init__(*args)
        self.form = form


def register_lead_user(first_name: str, email: str, source: str) -> User:
    """
    Create a new user on the system generation a random password.
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: User
    """
    data = {'first_name': first_name, 'email': email, 'source': source}

    form = UserSignupForm(data)
    if not form.is_valid():
        raise UserCreationException(form)
    user = form.save()
    assign_role(user, 'lead')
    return user
