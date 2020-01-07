from datetime import datetime
from typing import List

import pytest
import pytz
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from model_mommy import mommy

from pythonpro.dashboard.models import TopicInteraction
from pythonpro.dashboard.templatetags.dashboard_tags import duration
from pythonpro.django_assertions import dj_assert_contains
from pythonpro.modules.models import Topic


@pytest.fixture
def interactions(logged_user, topic):
    with freeze_time("2019-07-22 00:00:00"):
        first_interaction = mommy.make(
            TopicInteraction,
            user=logged_user,
            topic=topic,
            topic_duration=125,
            total_watched_time=125,
            max_watched_time=95
        )

    with freeze_time("2019-07-22 01:00:00"):
        second_interaction = mommy.make(
            TopicInteraction,
            user=logged_user,
            topic=topic,
            topic_duration=125,
            total_watched_time=34,
            max_watched_time=14
        )
    with freeze_time("2019-07-22 00:30:00"):
        third_interaction = mommy.make(
            TopicInteraction,
            user=logged_user,
            topic=topic,
            topic_duration=125,
            total_watched_time=64,
            max_watched_time=34
        )
    return [
        first_interaction,
        second_interaction,
        third_interaction,
    ]


@pytest.fixture
def resp(client_with_lead, interactions):
    return client_with_lead.get(
        reverse('dashboard:home'),
        secure=True
    )


def test_status_code(resp):
    return resp.status_code == 200


def test_topic_title_is_present(resp, topic):
    dj_assert_contains(resp, topic.title)


def test_table_instructions(resp, topic):
    dj_assert_contains(resp, 'Confira os dados consolidados por tópico')


def test_topic_url(resp, topic: Topic):
    dj_assert_contains(resp, topic.get_absolute_url())


def test_module_table_row(resp, topic: Topic):
    module = topic.find_module()
    dj_assert_contains(resp, f'<td><a href="{module.get_absolute_url()}">{module.title}</a></td>')


def test_max_creation(resp, interactions):
    tz = timezone.get_current_timezone()
    last_interaction_utc = datetime(2019, 7, 22, 1, 0, 0, tzinfo=pytz.utc)
    last_interaction_local = last_interaction_utc.astimezone(tz).strftime('%d/%m/%Y %H:%M:%S')
    dj_assert_contains(resp, last_interaction_local)


def test_max_watched_time(resp, interactions: List[TopicInteraction]):
    max_watched_time = max(interaction.max_watched_time for interaction in interactions)
    max_watched_time_str = duration(max_watched_time)
    dj_assert_contains(resp, max_watched_time_str)


def test_total_watched_time(resp, interactions: List[TopicInteraction]):
    total_watched_time = sum(interaction.total_watched_time for interaction in interactions)
    total_watched_time_str = duration(total_watched_time)
    dj_assert_contains(resp, total_watched_time_str)


def test_interactions_count(resp, interactions: List[TopicInteraction]):
    interactions_count = len(interactions)
    dj_assert_contains(resp, f'<td>{interactions_count}</td>')


@pytest.fixture
def resp_without_interactions(client_with_lead):
    return client_with_lead.get(
        reverse('dashboard:home'),
        secure=True
    )


def test_not_existing_aggregation_msg_is_present(resp_without_interactions, topic):
    dj_assert_contains(resp_without_interactions, "Ainda não existem dados agregados")
