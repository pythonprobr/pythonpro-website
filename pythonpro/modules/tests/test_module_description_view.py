import pytest
from django.core.management import call_command
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Module


@pytest.fixture
def module(db):
    call_command('loaddata', 'pythonpro_modules.json')
    return Module.objects.first()


@pytest.fixture
def resp(client, module):
    return client.get(reverse('modules:description', kwargs={'slug': module.slug}))


def test_status_code(resp):
    assert resp.status_code == 200


def test_module_title(resp, module):
    dj_assert_contains(resp, module.title)


def test_module_objective(resp, module):
    dj_assert_contains(resp, module.objective)


def test_module_target(resp, module):
    pass


def test_module_description(resp, module):
    dj_assert_contains(resp, module.description)


def test_module_section_chapter_description(resp, module):
    for section in module.section_set.all():
        for chapter in section.chapters:
            dj_assert_contains(resp, chapter.title)
