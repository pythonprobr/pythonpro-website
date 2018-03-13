import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.modules.models import modules
from pythonpro.modules.models.modules import Module
from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains


@pytest.fixture
def resp(client, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return resp_not_logged(client)


@pytest.fixture
def resp_not_logged(client):
    return client.get(reverse('modules:index'))


modules_dec = pytest.mark.parametrize('module', modules.ALL.values())


def test_status_code_logged(resp):
    assert resp.status_code == 200


def test_status_code_not_logged(resp_not_logged):
    assert resp_not_logged.status_code == 200


def test_module_index_link_not_logged(resp_not_logged):
    """ Assert module index link is present when user is not logged """
    url = reverse('modules:index')
    dj_assert_contains(resp_not_logged, f'href="{url}"')


@modules_dec
def test_module_link_not_logged(module: Module, resp_not_logged):
    """ Assert module links are not present when user is not logged """
    dj_assert_not_contains(resp_not_logged, f'href="{module.url()}"')


def test_module_index_link_logged(resp):
    """ Assert module index link is not present when user is logged """
    url = reverse('modules:index')
    dj_assert_not_contains(resp, f'href="{url}"')


@modules_dec
def test_module_link_logged(module: Module, resp):
    """ Assert module links are present when user is logged """
    dj_assert_contains(resp, f'href="{module.url()}"')


@modules_dec
def test_anchor(module, resp_not_logged):
    dj_assert_contains(resp_not_logged, f'<h1 id="{module.slug}"')


@modules_dec
def test_title(module, resp_not_logged):
    dj_assert_contains(resp_not_logged, module.title)


@modules_dec
def test_objective(module: Module, resp_not_logged):
    dj_assert_contains(resp_not_logged, module.objective)


@modules_dec
def test_descritption(module: Module, resp_not_logged):
    dj_assert_contains(resp_not_logged, module.description)


@modules_dec
def test_target(module: Module, resp_not_logged):
    dj_assert_contains(resp_not_logged, module.target)
