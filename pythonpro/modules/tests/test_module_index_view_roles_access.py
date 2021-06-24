import pytest
from django.core.management import call_command
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
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
