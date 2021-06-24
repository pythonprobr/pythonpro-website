import pytest
from django.urls import reverse
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains
from pythonpro.modules.models import Chapter, Module, Section, Topic


@pytest.fixture
def module(db):
    return baker.make(Module, slug='python-birds')


@pytest.fixture
def section(module):
    return baker.make(Section, module=module)


@pytest.fixture
def chapter(section):
    return baker.make(Chapter, section=section)


@pytest.fixture
def topics(chapter):
    return [baker.make(Topic, chapter=chapter, order=i) for i in range(2)]


@pytest.fixture
def resp(client_with_member, django_user_model, topics):
    next_topic = topics[1]
    return client_with_member.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': next_topic.module_slug(), 'topic_slug': next_topic.slug}),
        secure=True)


@pytest.fixture
def resp_first_topic(client_with_member, topics, logged_user):
    first_topic = topics[0]
    yield client_with_member.get(
        reverse(
            'modules:topic_detail', kwargs={'module_slug': first_topic.module_slug(), 'topic_slug': first_topic.slug}
        ),
        secure=True
    )


def test_topic_with_previous_topic(resp, topics):
    previous_topic, _ = topics
    dj_assert_contains(resp, previous_topic.get_absolute_url())


def test_first_topic(resp_first_topic):
    dj_assert_not_contains(resp_first_topic, 'Conteúdo Anterior')


def test_first_topic_previous_chapter(section):
    """Assert previous Chapter as previous content for the first Topic"""
    previous_chapter, next_chapter = [baker.make(Chapter, section=section, order=order) for order in range(2)]
    topic = baker.make(Topic, chapter=next_chapter)
    assert previous_chapter == topic.previous_content()


def test_topic_previous_section(module):
    """Assert previous Section as previous content for the first Topic"""
    previous_section, next_section = [baker.make(Section, module=module, order=order) for order in range(2)]
    chapter = baker.make(Chapter, section=next_section)
    topic = baker.make(Topic, chapter=chapter)
    assert previous_section == topic.previous_content()


@pytest.mark.django_db
def test_topic_previous_module():
    """Assert previous Module as previous content for the first Topic"""
    previous_module, next_module = [baker.make(Module, order=order) for order in range(2)]
    section = baker.make(Section, module=next_module)
    chapter = baker.make(Chapter, section=section)
    topic = baker.make(Topic, chapter=chapter)
    assert previous_module == topic.previous_content()


def test_previous_topic_first_none(chapter):
    """Assert None as previous content for the First Topic of First Chapter of First Section of First Module"""
    topic = baker.make(Topic, chapter=chapter)
    assert topic.previous_content() is None


def test_cache(chapter, mocker):
    """Assert cache is used when calling previous content multiple times"""
    topic = baker.make(Topic, chapter=chapter)
    mocker.spy(topic, '_previous_content_query_set')
    for _ in range(3):
        topic.previous_content()
    assert topic._previous_content_query_set.call_count == 1
