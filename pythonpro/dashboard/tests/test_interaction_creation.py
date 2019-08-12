import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.dashboard.models import TopicInteraction
from pythonpro.domain import user_facade


@pytest.fixture
def remove_tags_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._mailchimp_facade.remove_tags')


@pytest.fixture
def resp(client_with_lead, topic, logged_user, remove_tags_mock):
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


@pytest.fixture
def resp_with_interaction(client_with_lead, topic, logged_user, remove_tags_mock):
    mommy.make(TopicInteraction, user=logged_user, topic=topic)
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


def test_user_mark_on_mainchimp(resp, remove_tags_mock, logged_user):
    remove_tags_mock.assert_called_once_with(logged_user.email, 'never-watched-video')


def test_user_activation(resp, remove_tags_mock, logged_user):
    assert 'ACTIVATED' == user_facade.find_user_interactions(logged_user)[0].category


def test_user_not_first_video(resp_with_interaction, remove_tags_mock):
    assert remove_tags_mock.call_count == 0


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
