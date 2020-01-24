import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.dashboard import facade
from pythonpro.dashboard.models import TopicInteraction
from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Chapter, Module, Section, Topic


# @pytest.fixture
# def interactions(logged_user, topic):
#     with freeze_time("2019-07-22 00:00:00"):
#         first_interaction = mommy.make(
#             TopicInteraction,
#             user=logged_user,
#             topic=topic,
#             topic_duration=125,
#             total_watched_time=125,
#             max_watched_time=95
#         )
#
#     with freeze_time("2019-07-22 01:00:00"):
#         second_interaction = mommy.make(
#             TopicInteraction,
#             user=logged_user,
#             topic=topic,
#             topic_duration=125,
#             total_watched_time=34,
#             max_watched_time=14
#         )
#     with freeze_time("2019-07-22 00:30:00"):
#         third_interaction = mommy.make(
#             TopicInteraction,
#             user=logged_user,
#             topic=topic,
#             topic_duration=125,
#             total_watched_time=64,
#             max_watched_time=34
#         )
#     return [
#         first_interaction,
#         second_interaction,
#         third_interaction,
#     ]


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


@pytest.fixture
def topics(chapters):
    models = []
    for c in chapters:
        models.extend(mommy.make(Topic, 2, chapter=c))
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
                topic_duration=100,
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


def test_module_percentage_style_on_card(resp, logged_user):
    for m in facade.calculate_module_progresses(logged_user):
        dj_assert_contains(resp, f'style="width: {m.progress:.0%}"')
