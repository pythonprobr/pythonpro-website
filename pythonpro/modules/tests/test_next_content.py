import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains
from pythonpro.modules.models import Section, Module, Chapter, Topic


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
def resp(client, django_user_model, chapter, topics):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client.get(reverse('topics:detail', kwargs={'slug': topics[0].slug}))


@pytest.fixture
def resp_last_topic(client, django_user_model, chapter, topics):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client.get(reverse('topics:detail', kwargs={'slug': topics[1].slug}))


def test_topic_with_next_topic(resp, topics):
    current_topic, next_topic = topics
    dj_assert_contains(resp, next_topic.get_absolute_url())


def test_last_topic(resp_last_topic, topics):
    dj_assert_not_contains(resp_last_topic, 'Próximo Tópico')
