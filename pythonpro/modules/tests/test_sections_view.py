import pytest
from django.urls import reverse
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Module, Section, Chapter, Topic


@pytest.fixture
def module():
    return baker.make(Module)


@pytest.fixture
def section(module):
    return baker.make(Section, slug='procedural', module=module)


@pytest.fixture
def resp_old_path(client_with_lead, section, django_user_model):
    return client_with_lead.get(
        reverse('sections:detail_old', kwargs={'slug': section.slug}))


def test_redirect_status_code(resp_old_path):
    assert resp_old_path.status_code == 301


def test_redirect_url(resp_old_path, section):
    assert resp_old_path.url == section.get_absolute_url()


@pytest.fixture
def resp(client_with_lead, section: Section):
    return _resp_section_detail(client_with_lead, section)


def _resp_section_detail(client, section):
    return client.get(reverse(
        'modules:section_detail',
        kwargs={'section_slug': section.slug, 'module_slug': section.module_slug()}),
        secure=True)


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


@pytest.fixture
def chapters(section):
    return baker.make(Chapter, 2, section=section)


@pytest.fixture
def resp_with_chapters(client_with_lead, section, chapters):
    return _resp_section_detail(client_with_lead, section)


def test_chapter_titles(resp_with_chapters, chapters):
    for chapter in chapters:
        dj_assert_contains(resp_with_chapters, chapter.title)


def test_chapter_urls(resp_with_chapters, chapters):
    for chapter in chapters:
        dj_assert_contains(resp_with_chapters, chapter.get_absolute_url())


@pytest.fixture
def topics(chapters):
    result = []
    for chapter in chapters:
        result.extend(baker.make(Topic, 2, chapter=chapter))
    return result


@pytest.fixture
def resp_with_topics(client_with_lead, section, topics):
    return _resp_section_detail(client_with_lead, section)


def test_topic_titles(resp_with_topics, topics):
    for topic in topics:
        dj_assert_contains(resp_with_topics, topic.title)


def test_topic_urls(resp_with_topics, topics):
    for topic in topics:
        dj_assert_contains(resp_with_topics, topic.get_absolute_url())
