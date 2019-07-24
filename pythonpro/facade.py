"""
Module working as a facade to all business rules from the entire system.
It must interact only with app's internal facades and can be used by views, CLI and other interfaces
"""
from pythonpro.core import facade as _core_facade
from pythonpro.core.models import User as _User

# exposing exception on Facade

UserCreationException = _core_facade.UserCreationException


def register_lead(first_name: str, email: str, source: str = 'unknown') -> _User:
    """
    Create a new user on the system generation a random password.
    An Welcome email is sent to the user informing his password with the link to change it.
    User is also registered on Mailchimp and subscribed to LeadWorkflow
    :param first_name: User's first name
    :param email: User's email
    :param source: source of User traffic
    :return: ser
    """
    if not source:
        source = 'unknown'
    return _core_facade.register_lead_user(first_name, email, source)
