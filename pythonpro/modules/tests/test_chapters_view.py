import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Section, Module, Chapter


@pytest.fixture
def module(db):
    return mommy.make(Module)


@pytest.fixture
def section(module):
    return mommy.make(Section, module=module)


@pytest.fixture
def chapter(section):
    return mommy.make(Chapter, section=section)


@pytest.fixture
def chapters(section):
    return mommy.make(Chapter, 2, section=section)


@pytest.fixture
def resp_section(client, django_user_model, section, chapters):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client.get(reverse('sections:detail', kwargs={'slug': section.slug}))


def test_chapter_title_on_section(resp_section, chapters):
    for chapter in chapters:
        dj_assert_contains(resp_section, chapter.title)


def test_chapter_url_on_section(resp_section, chapters):
    for chapter in chapters:
        dj_assert_contains(resp_section, chapter.get_absolute_url())


@pytest.fixture
def resp(client, chapter, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client.get(reverse('chapters:detail', kwargs={'slug': chapter.slug}))


def test_status_code(resp):
    assert resp.status_code == 200


def test_breadcrumb_module(resp, module):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item"><a href="{module.get_absolute_url()}">{module.title}</a></li>'
    )


def test_breadcrumb_section(resp, section):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item"><a href="{section.get_absolute_url()}">{section.title}</a></li>'
    )
#
#
# def test_breadcrumb_current(resp, section):
#     dj_assert_contains(
#         resp,
#         f'<li class="breadcrumb-item active" aria-current="page">{section.title}</li>'
#     )
