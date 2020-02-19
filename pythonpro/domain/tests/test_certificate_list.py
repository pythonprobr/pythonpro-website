from typing import List

import pytest
from django.urls import reverse
from model_mommy import mommy

import pythonpro.domain.content_statistics_domain
from pythonpro.dashboard.models import TopicInteraction
from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Chapter, Module, Section, Topic


# Tests user interacted with all topics
@pytest.fixture
def modules(db):
    return mommy.make(Module, 2)


@pytest.fixture
def sections(modules):
    models = []
    for m in modules:
        models.extend(mommy.make(Section, 2, module=m))
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
                total_watched_time=100,
                max_watched_time=50
            )
        )
    return models


@pytest.fixture
def resp(client_with_lead, interactions):
    return client_with_lead.get(
        reverse('dashboard:home'),
        secure=True
    )


def test_module_title_is_present_on_card(resp, modules):
    for m in modules:
        dj_assert_contains(resp, f'Módulo: {m.title}')


def test_module_certificate_link(resp, modules: List[Module]):
    for m in modules:
        dj_assert_contains(resp, f'href="{m.get_certificate_url()}"')


def test_module_percentage_style_on_card(resp, logged_user):
    for m in pythonpro.domain.content_statistics_domain.calculate_modules_progresses(logged_user):
        dj_assert_contains(resp, f'style="width: {m.progress:.0%}"')


def test_module_duration(resp, logged_user):
    modules_progresses = resp.context['module_progresses']
    for module in modules_progresses:
        assert module.duration == module.topics_count * TOPIC_DURATION


# Tests User has not interaction with topics
@pytest.fixture
def resp_user_has_no_interactions(client_with_lead, topics):
    return client_with_lead.get(reverse('dashboard:home'), secure=True)


def test_module_duration_with_no_interactions(resp_user_has_no_interactions, logged_user, ):
    modules_progresses = resp_user_has_no_interactions.context['module_progresses']
    for module in modules_progresses:
        assert module.duration == module.topics_count * TOPIC_DURATION
