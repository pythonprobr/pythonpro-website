from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from model_mommy import mommy

from pythonpro.cohorts.models import Cohort, LiveClass
from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains


@pytest.fixture
def live_class(db, cohort, fake) -> LiveClass:
    now = timezone.now()
    return mommy.make(
        LiveClass,
        cohort=cohort,
        vimeo_id='1212',
        start=now + timedelta(days=1),
        description=fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)
    )


@pytest.fixture
def resp(client_with_member, live_class: LiveClass):
    return client_with_member.get(reverse('cohorts:live_class', kwargs={'pk': live_class.id}), secure=True)


def test_logged_user(resp):
    assert resp.status_code == 200


def test_link_unavailable_for_non_users(client):
    resp = client.get(reverse('cohorts:live_class', kwargs={'pk': 1}), secure=True)
    assert resp.status_code == 302


@pytest.mark.parametrize('property_name', 'description vimeo_id discourse_topic_id'.split())
def test_basic_contents(resp, live_class, property_name):
    dj_assert_contains(resp, getattr(live_class, property_name))


def test_cohort_title(cohort, resp):
    dj_assert_contains(resp, cohort.title)


@pytest.fixture
def resp_video_not_recorded(client_with_member, live_class: LiveClass):
    live_class.vimeo_id = ''
    live_class.save()
    return client_with_member.get(reverse('cohorts:live_class', kwargs={'pk': live_class.id}), secure=True)


def test_pending_live_class_msg(resp_video_not_recorded):
    dj_assert_contains(
        resp_video_not_recorded,
        'Ainda não temos máquina do tempo, essa aula ainda não foi gravada'
    )

    dj_assert_contains(
        resp_video_not_recorded,
        'Retornar à página da turma'
    )


def test_vimeo_player_not_present(resp_video_not_recorded):
    dj_assert_not_contains(
        resp_video_not_recorded,
        'src="https://player.vimeo.com/video/"'
    )


@pytest.fixture
def resp_client(client_with_client, live_class: LiveClass, mocker, logged_user):
    return client_with_client.get(reverse('cohorts:live_class', kwargs={'pk': live_class.id}), secure=True)


def test_live_class_landing_for_client(cohort, resp_client):
    assert resp_client.status_code == 302
    assert resp_client.url == reverse('member_landing_page')


@pytest.fixture
def resp_lead(client_with_lead, live_class: LiveClass, mocker, logged_user):
    return client_with_lead.get(reverse('cohorts:live_class', kwargs={'pk': live_class.id}), secure=True)


def test_live_class_landing_for_lead(cohort, resp_lead):
    assert resp_lead.status_code == 302
    assert resp_lead.url == reverse('member_landing_page')


def test_cohort_url(cohort: Cohort, resp):
    dj_assert_contains(resp, cohort.get_absolute_url())
