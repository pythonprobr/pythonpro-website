import pytest
from django.conf import settings
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Section, Module, Chapter, Topic


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
def topics(chapter):
    return mommy.make(Topic, 2, chapter=chapter)


@pytest.fixture
def topic(chapter):
    return mommy.make(Topic, chapter=chapter)


@pytest.fixture
def resp_chapter(client, django_user_model, chapter, topics):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client.get(reverse('chapters:detail', kwargs={'slug': chapter.slug}))


def test_topic_title_on_chapter(resp_chapter, topics):
    for topic in topics:
        dj_assert_contains(resp_chapter, topic.title)


def test_topic_url_on_section(resp_chapter, topics):
    for topic in topics:
        dj_assert_contains(resp_chapter, topic.get_absolute_url())


@pytest.fixture
def resp(client, topic, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client.get(reverse('topics:detail', kwargs={'slug': topic.slug}))


def test_status_code(resp):
    assert resp.status_code == 200


def test_vimeo_video(resp, topic):
    dj_assert_contains(resp, f'<iframe src="https://player.vimeo.com/video/{ topic.vimeo_id }"')


@pytest.mark.parametrize('property_name', 'title description'.split())
def test_property_is_present(resp, topic, property_name):
    dj_assert_contains(resp, getattr(topic, property_name))


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


def test_breadcrumb_chapter(resp, chapter):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item"><a href="{chapter.get_absolute_url()}">{chapter.title}</a></li>'
    )


def test_breadcrumb_current(resp, topic):
    dj_assert_contains(
        resp,
        f'<li class="breadcrumb-item active" aria-current="page">{topic.title}</li>'
    )


def test_discourse_topic_id(resp, topic):
    dj_assert_contains(resp, f"topicId: {topic.discourse_topic_id}")


def test_discourse_url(resp, topic):
    dj_assert_contains(resp, f"discourseUrl: '{settings.DISCOURSE_BASE_URL}'")
