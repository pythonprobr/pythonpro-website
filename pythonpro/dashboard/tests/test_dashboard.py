import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.dashboard.models import TopicInteraction
from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def interactions(logged_user, topic):
    return mommy.make(TopicInteraction, 100, user=logged_user, topic=topic)


@pytest.fixture
def resp(client_with_lead, interactions):
    return client_with_lead.get(
        reverse('dashboard:home'),
        secure=True
    )


def test_topic_interaction_status_code(resp):
    return resp.status_code == 200


def test_topic_url_is_present(resp, topic):
    dj_assert_contains(resp, reverse('topics:detail', kwargs={'slug': topic.slug}))


def test_topic_title_is_present(resp, topic):
    dj_assert_contains(resp, topic.title)
