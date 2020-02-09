import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.dashboard.models import TopicInteraction
from pythonpro.dashboard.templatetags.dashboard_tags import duration
from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Chapter, Module, Section, Topic


# Tests user interacted with all topics
@pytest.fixture
def module(db):
    return mommy.make(Module)


@pytest.fixture
def sections(module):
    models = []
    models.extend(mommy.make(Section, 2, module=module))
    return models


@pytest.fixture
def chapters(sections):
    models = []
    for s in sections:
        models.extend(mommy.make(Chapter, 2, section=s))
    return models


TOPIC_DURATION = 100


@pytest.fixture
def topics(chapters):
    models = []
    for c in chapters:
        models.extend(mommy.make(Topic, 2, chapter=c, duration=TOPIC_DURATION))
    return models


@pytest.fixture
def interactions(topics, logged_user):
    models = []
    for t in topics:
        models.append(
            mommy.make(
                TopicInteraction,
                user=logged_user,
                topic=t,
                topic_duration=TOPIC_DURATION,
                total_watched_time=TOPIC_DURATION // 4,
                max_watched_time=TOPIC_DURATION // 2
            )
        )
    return models


@pytest.fixture
def resp(client_with_lead, interactions, module):
    return client_with_lead.get(
        reverse('dashboard:certificate', kwargs={'module_slug': module.slug}),
        secure=True
    )


def test_status_code(resp, module):
    assert resp.status_code == 200


def test_module_title_is_present(resp, module):
    dj_assert_contains(resp, module.title)


def test_user_name_is_present(resp, logged_user):
    dj_assert_contains(resp, logged_user.first_name)


def test_user_progress(resp):
    dj_assert_contains(resp, 'concluiu 50%')


def test_user_watched_time(resp, interactions):
    dj_assert_contains(resp, duration(len(interactions) * TOPIC_DURATION // 4))


def test_module_total_duration(resp, topics):
    dj_assert_contains(resp, duration(len(topics) * TOPIC_DURATION))


def test_finished_topics(resp):
    dj_assert_contains(resp, 'finalizado 0 aulas')


def test_total_topis(resp, topics):
    dj_assert_contains(resp, f'total de {len(topics)}')
