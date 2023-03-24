import pytest
from django.urls import reverse
from model_bakery import baker

from pythonpro.dashboard.models import TopicInteraction
from pythonpro.domain import user_domain
from pythonpro.modules.models import Topic


@pytest.fixture
def remove_tags_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.remove_tags.delay')


@pytest.fixture
def tag_newly_completed_contents_mock(mocker):
    return mocker.patch('pythonpro.dashboard.views.content_statistics_domain.tag_newly_completed_contents.delay')


TOPIC_DURATION = 200


@pytest.fixture
def resp(client_with_lead, topic, logged_user, remove_tags_mock, tag_newly_completed_contents_mock):
    return client_with_lead.post(
        reverse('dashboard:topic_interaction'),
        data={
            'topic': topic.id,
            'topic_duration': TOPIC_DURATION,
            'total_watched_time': 120,
            'max_watched_time': 60
        },
        secure=True
    )


@pytest.fixture
def resp_with_interaction(client_with_lead, topic, logged_user, remove_tags_mock, tag_newly_completed_contents_mock):
    baker.make(TopicInteraction, user=logged_user, topic=topic)
    return client_with_lead.post(
        reverse('dashboard:topic_interaction'),
        data={
            'topic': topic.id,
            'topic_duration': TOPIC_DURATION,
            'total_watched_time': 120,
            'max_watched_time': 60
        },
        secure=True
    )


def test_user_mark_on_email_marketing(resp, remove_tags_mock, logged_user):
    remove_tags_mock.assert_called_once_with(logged_user.email, logged_user.id, 'never-watched-video')


def test_user_activation(resp, remove_tags_mock, logged_user):
    assert 'ACTIVATED' == user_domain.find_user_interactions(logged_user)[0].category


def test_topic_interaction_status_code(resp):
    assert resp.status_code == 200


def test_topic_interaction_is_created(resp):
    assert TopicInteraction.objects.exists()


def test_topic_interaction_data(resp, topic, logged_user):
    interaction = TopicInteraction.objects.first()
    assert interaction.topic == topic
    assert interaction.user == logged_user
    assert interaction.topic_duration == TOPIC_DURATION
    assert interaction.total_watched_time == 120
    assert interaction.max_watched_time == 60


def test_topic_is_updated(resp, topic, logged_user):
    assert Topic.objects.values('duration').get(id=topic.id)['duration'] == TOPIC_DURATION


def test_user_not_first_video(resp_with_interaction, remove_tags_mock):
    assert remove_tags_mock.call_count == 0


def test_tag_as_not_called_with_uncomplete_contents(resp, tag_newly_completed_contents_mock):
    assert tag_newly_completed_contents_mock.call_count == 0


@pytest.fixture
def resp_complete_content(client_with_lead, topic, logged_user, remove_tags_mock, tag_newly_completed_contents_mock):
    return client_with_lead.post(
        reverse('dashboard:topic_interaction'),
        data={
            'topic': topic.id,
            'topic_duration': TOPIC_DURATION,
            'total_watched_time': TOPIC_DURATION,
            'max_watched_time': TOPIC_DURATION
        },
        secure=True
    )


def test_tag_as_called_with_complete_contents(
        resp_complete_content, tag_newly_completed_contents_mock, logged_user,
        module, section, chapter, topic):
    tag_newly_completed_contents_mock.assert_called_once_with(logged_user.id, topic.id)
