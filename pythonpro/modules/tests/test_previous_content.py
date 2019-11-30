import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains
from pythonpro.modules.models import Chapter, Module, Section, Topic


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
    return [mommy.make(Topic, chapter=chapter, order=i) for i in range(2)]


@pytest.fixture
def resp(client_with_member, django_user_model, topics):
    previous_topic = topics[0]
    return client_with_member.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': previous_topic.module_slug(), 'topic_slug': previous_topic.slug}),
        secure=True)


@pytest.fixture
def resp_last_topic(client_with_member, topics, logged_user):
    first_topic = topics[1]
    yield client_with_member.get(
        reverse(
            'modules:topic_detail', kwargs={'module_slug': first_topic.module_slug(), 'topic_slug': first_topic.slug}
        ),
        secure=True
    )


def test_topic_with_previous_topic(resp, topics):
    previous_topic, first_topic = topics
    dj_assert_contains(resp, first_topic.get_absolute_url())


def test_first_topic(resp_last_topic):
    dj_assert_not_contains(resp_last_topic, 'Conteúdo Anterior')


def test_previous_topic_first_chapter(section):
    """Assert previous Chapter as previous content for the First Topic"""
    previous_chapter, first_chapter = [mommy.make(Chapter, section=section, order=order) for order in range(2)]
    topic = mommy.make(Topic, chapter=previous_chapter)
    assert first_chapter == topic.next_content()


def test_previous_topic_first_section(module):
    """Assert previous Section as previous content for the first Topic of first Chapter"""
    previous_section, first_section = [mommy.make(Section, module=module, order=order) for order in range(2)]
    chapter = mommy.make(Chapter, section=previous_section)
    topic = mommy.make(Topic, chapter=chapter)
    assert first_section == topic.next_content()


@pytest.mark.django_db
def test_previous_topic_first_module():
    """Assert previous Module as previous content for the first Topic of first Chapter of first Section"""
    previous_module, first_module = [mommy.make(Module, order=order) for order in range(2)]
    section = mommy.make(Section, module=previous_module)
    chapter = mommy.make(Chapter, section=section)
    topic = mommy.make(Topic, chapter=chapter)
    assert first_module == topic.next_content()


def test_previous_topic_first_none(chapter):
    """Assert None as previous content for the First Topic of First Chapter of First Section of First Module"""
    topic = mommy.make(Topic, chapter=chapter)
    assert topic.previous_content() is None


def test_cache(chapter, mocker):
    """Assert cache is used when calling previous content multiple times"""
    topic = mommy.make(Topic, chapter=chapter)
    mocker.spy(topic, '_previous_content_query_set')
    for _ in range(3):
        topic.previous_content()
    assert topic._previous_content_query_set.call_count == 1
