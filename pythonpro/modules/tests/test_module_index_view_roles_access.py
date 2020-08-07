import pytest
from django.core.management import call_command
from django.urls import reverse
from model_bakery import baker
from rolepermissions.roles import assign_role, clear_roles

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains
from pythonpro.modules import facade


@pytest.fixture
def modules(transactional_db):
    call_command('loaddata', 'pythonpro_modules.json')
    modules = facade.get_all_modules()
    return modules


@pytest.fixture
def resp_lead_user(client, django_user_model, modules):
    user = baker.make(django_user_model)
    clear_roles(user)
    assign_role(user, 'lead')
    client.force_login(user)
    return _resp_not_logged(client, modules)


@pytest.fixture
def resp_webdev_user(client, django_user_model, modules):
    user = baker.make(django_user_model)
    clear_roles(user)
    assign_role(user, 'webdev')
    client.force_login(user)
    return _resp_not_logged(client, modules)


@pytest.fixture
def resp_bootcamper_user(client, django_user_model, modules):
    user = baker.make(django_user_model)
    clear_roles(user)
    assign_role(user, 'bootcamper')
    client.force_login(user)
    return _resp_not_logged(client, modules)


@pytest.fixture
def resp_client_user(client, django_user_model, modules):
    user = baker.make(django_user_model)
    clear_roles(user)
    assign_role(user, 'client')
    client.force_login(user)
    return _resp_not_logged(client, modules)


@pytest.fixture
def resp_pythonista_user(client, django_user_model, modules):
    user = baker.make(django_user_model)
    clear_roles(user)
    assign_role(user, 'pythonista')
    client.force_login(user)
    return _resp_not_logged(client, modules)


def _resp_not_logged(client, modules):
    return client.get(reverse('modules:index'))


def test_module_lead_user_can_access(modules, resp_lead_user):
    """ Assert that user with a lead role can access the right content """
    dj_assert_contains(resp_lead_user, 'href="/modulos/python-birds/"')


@pytest.mark.parametrize('urls', [
    'href="/modulos/objetos-pythonicos/"',
    'href="/modulos/pytools/"',
    'href="/modulos/python-para-pythonistas/"',
    'href="/modulos/django/"',
    'href="/modulos/python-paterns/"',
    'href="/modulos/entrevistas-tecnicas/"',
])
def test_module_lead_user_can_not_access(modules, resp_lead_user, urls):
    """ Assert that user with a lead role can not access some contents """
    dj_assert_not_contains(resp_lead_user, urls)


@pytest.mark.parametrize('urls', [
    'href="/modulos/python-birds/"',
    'href="/modulos/pytools/"',
])
def test_module_client_user_can_access(modules, resp_client_user, urls):
    """ Assert that user with a client role can access the right content """
    dj_assert_contains(resp_client_user, urls)


@pytest.mark.parametrize('urls', [
    'href="/modulos/python-web/"',
    'href="/modulos/objetos-pythonicos/"',
    'href="/modulos/python-para-pythonistas/"',
    'href="/modulos/python-paterns/"',
    'href="/modulos/entrevistas-tecnicas/"',
])
def test_module_client_user_can_not_access(modules, resp_client_user, urls):
    """ Assert that user with a client role can not access some contents """
    dj_assert_not_contains(resp_client_user, urls)


@pytest.mark.parametrize('urls', [
    'href="/modulos/python-birds/"',
    'href="/modulos/pytools/"',
    'href="/modulos/python-web/"',
])
def test_module_webdev_user_can_access(modules, resp_webdev_user, urls):
    """ Assert that user with a webdev role can access the right content """
    dj_assert_contains(resp_webdev_user, urls)


@pytest.mark.parametrize('urls', [
    'href="/modulos/objetos-pythonicos/"',
    'href="/modulos/python-para-pythonistas/"',
    'href="/modulos/python-paterns/"',
    'href="/modulos/entrevistas-tecnicas/"',
])
def test_module_webdev_user_can_not_access(modules, resp_webdev_user, urls):
    """ Assert that user with a webdev role can not access some contents """
    dj_assert_not_contains(resp_webdev_user, urls)


@pytest.mark.parametrize('urls', [
    'href="/modulos/python-birds/"',
    'href="/modulos/pytools/"',
    'href="/modulos/python-web/"',
    'href="/modulos/entrevistas-tecnicas/"',
])
def test_module_bootcamper_user_can_access(modules, resp_bootcamper_user, urls):
    """ Assert that user with a bootcamper role can access the right content """
    dj_assert_contains(resp_bootcamper_user, urls)


@pytest.mark.parametrize('urls', [
    'href="/modulos/objetos-pythonicos/"',
    'href="/modulos/python-para-pythonistas/"',
    'href="/modulos/python-paterns/"',
])
def test_module_bootcamper_user_can_not_access(modules, resp_bootcamper_user, urls):
    """ Assert that user with a bootcamper role can not access some contents """
    dj_assert_not_contains(resp_bootcamper_user, urls)


@pytest.mark.parametrize('urls', [
    'href="/modulos/python-birds/"',
    'href="/modulos/objetos-pythonicos/"',
    'href="/modulos/python-para-pythonistas/"',
    'href="/modulos/python-patterns/"',
])
def test_module_pythonista_user_can_access(modules, resp_pythonista_user, urls):
    """ Assert that user with a pythonista role can access the right content """
    dj_assert_contains(resp_pythonista_user, urls)


@pytest.mark.parametrize('urls', [
    'href="/modulos/pytools/"',
    'href="/modulos/python-web/"',
    'href="/modulos/entrevistas-tecnicas/"',
])
def test_module_pythonista_user_can_not_access(modules, resp_pythonista_user, urls):
    """ Assert that user with a pythonista role can not access some contents """
    dj_assert_not_contains(resp_pythonista_user, urls)
