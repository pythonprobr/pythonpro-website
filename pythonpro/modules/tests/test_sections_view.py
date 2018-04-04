import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Section, Module


@pytest.fixture
def module():
    return mommy.make(Module)


@pytest.fixture
def section(module):
    return mommy.make(Section, slug='procedural', module=module)


@pytest.fixture
def resp(client, django_user_model, section):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client.get(reverse('sections:detail', kwargs={'slug': section.slug}))


def test_status_code(resp):
    assert resp.status_code == 200


@pytest.mark.parametrize('property_name', ['title', 'description'])
def test_title(resp, section, property_name):
    dj_assert_contains(resp, getattr(section, property_name))


def test_breadcrumb_parent(resp, module):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item"><a href="{module.get_absolute_url()}">{module.title}</a></li>'
    )


def test_breadcrumb_current(resp, section):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item active" aria-current="page">{section.title}</li>'
    )
