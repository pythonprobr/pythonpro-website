import pytest
from django.core.management import call_command
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains
from pythonpro.modules import facade


@pytest.fixture
def modules(transactional_db):
    call_command('loaddata', 'pythonpro_modules.json')
    modules = facade.get_all_modules()
    return modules


@pytest.fixture
def resp_lead_user(client_with_lead, modules):
    return _resp_not_logged(client_with_lead)


@pytest.fixture
def resp_webdev_user(client_with_webdev, modules):
    return _resp_not_logged(client_with_webdev)


@pytest.fixture
def resp_bootcamper_user(client_with_bootcamper, modules):
    return _resp_not_logged(client_with_bootcamper)


@pytest.fixture
def resp_client_user(client_with_client, modules):
    return _resp_not_logged(client_with_client)


@pytest.fixture
def resp_pythonista_user(client_with_pythonista, modules):
    return _resp_not_logged(client_with_pythonista)


@pytest.fixture
def resp_member_user(client_with_member, modules):
    return _resp_not_logged(client_with_member)


def _resp_not_logged(client):
    return client.get(reverse('modules:index'))


@pytest.fixture
def modules_dct(modules):
    return {m.slug: m for m in modules}


def test_module_lead_user_can_access(modules_dct, resp_lead_user):
    """ Assert that user with a lead role can access the right content """
    python_birds = modules_dct['python-birds']
    dj_assert_contains(resp_lead_user, f'href="{python_birds.get_absolute_url()}"')


@pytest.mark.parametrize('slug', [
    'objetos-pythonicos',
    'pytools',
    'python-para-pythonistas',
    'django',
    'python-patterns',
    'entrevistas-tecnicas',
])
def test_module_lead_user_can_not_access(modules_dct, resp_lead_user, slug):
    """ Assert that user with a lead role can not access some contents """
    dj_assert_not_contains(resp_lead_user, modules_dct[slug].get_absolute_url())


@pytest.mark.parametrize('slug', ['python-birds', 'pytools'])
def test_module_client_user_can_access(modules_dct, resp_client_user, slug):
    """ Assert that user with a client role can access the right content """
    dj_assert_contains(resp_client_user, modules_dct[slug].get_absolute_url())


@pytest.mark.parametrize('slug', [
    'django',
    'objetos-pythonicos',
    'python-para-pythonistas',
    'python-patterns',
    'entrevistas-tecnicas',
])
def test_module_client_user_can_not_access(modules_dct, resp_client_user, slug):
    """ Assert that user with a client role can not access some contents """
    dj_assert_not_contains(resp_client_user, modules_dct[slug].get_absolute_url())


@pytest.mark.parametrize('slug', [
    'python-birds',
    'pytools',
    'django',
    'entrevistas-tecnicas',
])
def test_module_webdev_user_can_access(modules_dct, resp_webdev_user, slug):
    """ Assert that user with a webdev role can access the right content """
    dj_assert_contains(resp_webdev_user, modules_dct[slug].get_absolute_url())


@pytest.mark.parametrize('slug', [
    'objetos-pythonicos',
    'python-para-pythonistas',
    'python-patterns',
])
def test_module_webdev_user_can_not_access(modules_dct, resp_webdev_user, slug):
    """ Assert that user with a webdev role can not access some contents """
    dj_assert_not_contains(resp_webdev_user, modules_dct[slug].get_absolute_url())


@pytest.mark.parametrize('slug', [
    'python-birds',
    'pytools',
    'django',
    'entrevistas-tecnicas',
    'objetos-pythonicos',
    'python-para-pythonistas',
    'python-patterns',
])
def test_module_bootcamper_user_can_access(modules_dct, resp_bootcamper_user, slug):
    """ Assert that user with a bootcamper role can access the right content """
    dj_assert_contains(resp_bootcamper_user, modules_dct[slug].get_absolute_url())


@pytest.mark.parametrize('slug', [
    'python-birds',
    'objetos-pythonicos',
    'python-para-pythonistas',
    'python-patterns',
])
def test_module_pythonista_user_can_access(modules_dct, resp_pythonista_user, slug):
    """ Assert that user with a pythonista role can access the right content """
    dj_assert_contains(resp_pythonista_user, modules_dct[slug].get_absolute_url())


@pytest.mark.parametrize('slug', [
    'pytools',
    'django',
    'entrevistas-tecnicas',
])
def test_module_pythonista_user_can_not_access(modules_dct, resp_pythonista_user, slug):
    """ Assert that user with a pythonista role can not access some contents """
    dj_assert_not_contains(resp_pythonista_user, modules_dct[slug].get_absolute_url())


@pytest.mark.parametrize('slug', [
    'pytools',
    'django',
    'entrevistas-tecnicas',
    'python-birds',
    'objetos-pythonicos',
    'python-para-pythonistas',
    'python-patterns',
])
def test_module_member_user_can_access(modules_dct, resp_member_user, slug):
    """ Assert that user with a member role can access all the content """
    dj_assert_contains(resp_member_user, modules_dct[slug].get_absolute_url())
