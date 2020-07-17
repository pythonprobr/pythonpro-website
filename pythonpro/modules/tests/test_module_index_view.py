import pytest
from django.core.management import call_command
from django.urls import reverse
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains
from pythonpro.modules import facade


@pytest.fixture
def modules(transactional_db):
    call_command('loaddata', 'pythonpro_modules.json')
    modules = facade.get_all_modules()
    return modules


@pytest.fixture
def resp(client, django_user_model, modules):
    user = baker.make(django_user_model)
    client.force_login(user)
    return _resp_not_logged(client, modules)


@pytest.fixture
def resp_not_logged(client, modules):
    return _resp_not_logged(client, modules)


def _resp_not_logged(client, modules):
    return client.get(reverse('modules:index'))


def test_status_code_logged(resp):
    assert resp.status_code == 200


def test_status_code_not_logged(resp_not_logged):
    assert resp_not_logged.status_code == 200


def test_module_index_link_not_logged(resp_not_logged):
    """ Assert module index link is present when user is not logged """
    url = reverse('modules:index')
    dj_assert_contains(resp_not_logged, f'href="{url}"')


def test_module_link_not_logged(modules, resp_not_logged):
    """ Assert module links are not present when user is not logged """
    for module in modules:
        dj_assert_not_contains(resp_not_logged, f'href="{module.get_absolute_url()}"')


def test_module_index_link_logged(resp):
    """ Assert module index link is not present when user is logged """
    url = reverse('modules:index')
    dj_assert_not_contains(resp, f'href="{url}"')


def test_module_link_logged(modules, resp):
    """ Assert module links are present when user is logged """
    for module in modules:
        dj_assert_contains(resp, f'href="{module.get_absolute_url()}"')


def test_anchor(modules, resp_not_logged):
    for module in modules:
        dj_assert_contains(resp_not_logged, f'<h1 id="{module.slug}"')


@pytest.mark.parametrize('attr_name', 'title objective description target'.split())
def test_present_attrs(modules, resp_not_logged, attr_name):
    for module in modules:
        dj_assert_contains(resp_not_logged, getattr(module, attr_name))
