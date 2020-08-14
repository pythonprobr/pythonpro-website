import pytest
from django.contrib.admin import AdminSite
from rolepermissions.checkers import has_role
from rolepermissions.roles import RolesManager

from pythonpro.core.admin import UserAdmin
from pythonpro.domain import user_domain


@pytest.fixture
def sync_user_delay(mocker):
    return mocker.patch('pythonpro.domain.user_domain.sync_user_on_discourse.delay')


@pytest.fixture
def email_market_mocks(mocker):
    maybe_function_names = dir(user_domain._email_marketing_facade)
    task_function_mocks = []
    for name in maybe_function_names:
        maybe_task_function = getattr(user_domain._email_marketing_facade, name)
        if hasattr(maybe_task_function, 'delay'):
            task_function_mocks.append(mocker.patch(
                f'pythonpro.domain.user_domain._email_marketing_facade.{name}.delay', side_effeict=maybe_task_function
            ))
    return task_function_mocks


@pytest.mark.parametrize('role', RolesManager.get_roles_names())
def test_make_actions(logged_user, role, django_user_model, sync_user_delay, email_market_mocks, cohort):
    if role in {'lead', 'client'}:
        return  # Client product is not active anymore
    admin = UserAdmin(django_user_model, AdminSite())
    make_method = getattr(admin, f'make_{role}')
    assert not has_role(logged_user, role)
    make_method(None, [logged_user])
    assert has_role(logged_user, role)
