import pytest
from django.urls import reverse

from pythonpro.dashboard.models import TopicInteraction


@pytest.fixture
def resp(client_with_lead, topic, logged_user):
    return client_with_lead.post(
        reverse('dashboard:topic_interaction'),
        data={
            'topic': topic.id,
            'topic_duration': 200,
            'total_watched_time': 120,
            'max_watched_time': 60
        },
        secure=True
    )


def test_topic_interaction_status_code(resp):
    return resp.status_code == 200


def test_topic_interaction_is_created(resp):
    assert TopicInteraction.objects.exists()


def test_topic_interaction_data(resp, topic, logged_user):
    interaction = TopicInteraction.objects.first()
    assert interaction.topic == topic
    assert interaction.user == logged_user
    assert interaction.topic_duration == 200
    assert interaction.total_watched_time == 120
    assert interaction.max_watched_time == 60
