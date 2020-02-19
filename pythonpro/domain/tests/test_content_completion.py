import pytest
from model_mommy import mommy

from pythonpro.dashboard.models import TopicInteraction
from pythonpro.domain import content_statistics_domain
from pythonpro.modules.models import Chapter, Module, Section, Topic

TOPIC_DURATION = 100


@pytest.fixture
def modules(db):
    return mommy.make(Module, 2)


@pytest.fixture
def sections(modules):
    models = []
    for module in modules:
        models.extend(mommy.make(Section, 2, module=module))
    return models


@pytest.fixture
def chapters(sections):
    models = []
    for s in sections:
        models.extend(mommy.make(Chapter, 2, section=s))
    return models


@pytest.fixture
def topics(chapters):
    models = []
    for c in chapters:
        models.extend(mommy.make(Topic, 2, chapter=c, duration=TOPIC_DURATION))
    return models


def _interactions(topics, logged_user, total_watched_time, max_watched_time):
    models = []
    for t in topics:
        models.append(
            mommy.make(
                TopicInteraction,
                user=logged_user,
                topic=t,
                topic_duration=TOPIC_DURATION,
                total_watched_time=total_watched_time,
                max_watched_time=max_watched_time
            )
        )
    return models


@pytest.fixture
def interactions_content_uncompleted(topics, logged_user):
    _interactions(topics, logged_user, total_watched_time=TOPIC_DURATION // 4, max_watched_time=TOPIC_DURATION // 2)


@pytest.fixture
def uncompleted_modules(db):
    return mommy.make(Module, 2)


@pytest.fixture
def uncompleted_sections(uncompleted_modules):
    models = []
    for module in uncompleted_modules:
        models.extend(mommy.make(Section, 2, module=module))
    return models


@pytest.fixture
def uncompleted_chapters(uncompleted_sections):
    models = []
    for s in uncompleted_sections:
        models.extend(mommy.make(Chapter, 2, section=s))
    return models


@pytest.fixture
def uncompleted_topics(uncompleted_chapters):
    models = []
    for c in uncompleted_chapters:
        models.extend(mommy.make(Topic, 2, chapter=c, duration=TOPIC_DURATION))
    return models


@pytest.fixture
def interactions_content_completed(topics, logged_user, uncompleted_topics) -> set:
    _interactions(topics, logged_user, total_watched_time=TOPIC_DURATION, max_watched_time=TOPIC_DURATION)


def extract_slug_set(contents):
    return {content.slug for content in contents}


def test_completed_modules_in_contents(modules, interactions_content_completed, logged_user, uncompleted_modules):
    contents = list(content_statistics_domain.completed_contents(logged_user))
    assert extract_slug_set(modules).issubset(extract_slug_set(contents))


def test_uncompleted_modules_not_in_contents(interactions_content_completed, logged_user, uncompleted_modules):
    contents = list(content_statistics_domain.completed_contents(logged_user))
    assert extract_slug_set(uncompleted_modules).isdisjoint(extract_slug_set(contents))


def test_completed_sections_in_contents(sections, interactions_content_completed, logged_user, uncompleted_sections):
    contents = list(content_statistics_domain.completed_contents(logged_user))
    assert extract_slug_set(sections).issubset(extract_slug_set(contents))


def test_uncompleted_sections_not_in_contents(interactions_content_completed, logged_user, uncompleted_sections):
    contents = list(content_statistics_domain.completed_contents(logged_user))
    assert extract_slug_set(uncompleted_sections).isdisjoint(extract_slug_set(contents))


def test_completed_chapters_in_contents(chapters, interactions_content_completed, logged_user, uncompleted_chapters):
    contents = list(content_statistics_domain.completed_contents(logged_user))
    assert extract_slug_set(chapters).issubset(extract_slug_set(contents))


def test_uncompleted_chapters_not_in_contents(interactions_content_completed, logged_user, uncompleted_chapters):
    contents = list(content_statistics_domain.completed_contents(logged_user))
    assert extract_slug_set(uncompleted_chapters).isdisjoint(extract_slug_set(contents))


def test_completed_topics_in_contents(topics, interactions_content_completed, logged_user, uncompleted_topics):
    contents = list(content_statistics_domain.completed_contents(logged_user))
    assert extract_slug_set(topics).issubset(extract_slug_set(contents))


def test_uncompleted_topics_not_in_contents(interactions_content_completed, logged_user, uncompleted_topics):
    contents = list(content_statistics_domain.completed_contents(logged_user))
    assert extract_slug_set(uncompleted_topics).isdisjoint(extract_slug_set(contents))


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.email_marketing.facade.tag_as')


def test_newly_all_completed_contents(topics, interactions_content_completed, logged_user, tag_as_mock):
    topic = topics[0]  # it can be anyone, so I chose first
    tags = [
        topic.chapter.section.module.full_slug,
        topic.chapter.section.full_slug,
        topic.chapter.full_slug,
        topic.full_slug,
    ]
    assert content_statistics_domain.tag_newly_completed_contents(logged_user, topic.id) == tags
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, *tags)


def test_newly_completed_topic(topics, logged_user, tag_as_mock):
    topic = topics[0]  # it can be anyone, so I chose first
    mommy.make(
        TopicInteraction,
        user=logged_user,
        topic=topic,
        topic_duration=TOPIC_DURATION,
        total_watched_time=TOPIC_DURATION,
        max_watched_time=TOPIC_DURATION
    )
    tags = [
        topic.full_slug,
    ]
    assert content_statistics_domain.tag_newly_completed_contents(logged_user, topic.id) == tags
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, *tags)
