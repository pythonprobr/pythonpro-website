import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules import PYTHON_BIRDS
from pythonpro.sections.models import Section


@pytest.fixture
def section():
    return mommy.make(Section, slug='procedural', _module_slug=PYTHON_BIRDS.slug)


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
