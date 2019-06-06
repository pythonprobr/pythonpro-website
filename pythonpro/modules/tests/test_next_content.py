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
    first_topic = topics[0]
    return client_with_member.get(
        reverse('modules:topic_detail',
                kwargs={'module_slug': first_topic.module_slug(), 'topic_slug': first_topic.slug}),
        secure=True)


@pytest.fixture
def resp_last_topic(client_with_member, topics, logged_user):
    last_topic = topics[1]
    yield client_with_member.get(
        reverse(
            'modules:topic_detail', kwargs={'module_slug': last_topic.module_slug(), 'topic_slug': last_topic.slug}
        ),
        secure=True
    )


def test_topic_with_next_topic(resp, topics):
    current_topic, next_topic = topics
    dj_assert_contains(resp, next_topic.get_absolute_url())


def test_last_topic(resp_last_topic):
    dj_assert_not_contains(resp_last_topic, 'Próximo Conteúdo')


def test_last_topic_next_chapter(section):
    """Assert next Chapter as next content for the last Topic"""
    first_chapter, next_chapter = [mommy.make(Chapter, section=section, order=order) for order in range(2)]
    topic = mommy.make(Topic, chapter=first_chapter)
    assert next_chapter == topic.next_content()


def test_last_topic_next_section(module):
    """Assert next Section as next content for the last Topic of last Chapter"""
    first_section, next_section = [mommy.make(Section, module=module, order=order) for order in range(2)]
    chapter = mommy.make(Chapter, section=first_section)
    topic = mommy.make(Topic, chapter=chapter)
    assert next_section == topic.next_content()


@pytest.mark.django_db
def test_last_topic_next_module():
    """Assert next Module as next content for the last Topic of last Chapter of last Section"""
    first_module, next_module = [mommy.make(Module, order=order) for order in range(2)]
    section = mommy.make(Section, module=first_module)
    chapter = mommy.make(Chapter, section=section)
    topic = mommy.make(Topic, chapter=chapter)
    assert next_module == topic.next_content()


def test_last_topic_next_none(chapter):
    """Assert None as next content for the last Topic of last Chapter of last Section of last Module"""
    topic = mommy.make(Topic, chapter=chapter)
    assert topic.next_content() is None


def test_cache(chapter, mocker):
    """Assert cache is used when calling next content multiple times"""
    topic = mommy.make(Topic, chapter=chapter)
    mocker.spy(topic, '_next_content_query_set')
    for _ in range(3):
        topic.next_content()
    assert topic._next_content_query_set.call_count == 1
