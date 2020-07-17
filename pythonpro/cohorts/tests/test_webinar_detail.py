import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_bakery import baker

from pythonpro.cohorts.models import Webinar
from pythonpro.cohorts.tests.conftest import img_path
from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains


@pytest.fixture
def webinar(cohort) -> Webinar:
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    return baker.make(Webinar, cohort=cohort, image=image, vimeo_id='1')


@pytest.fixture
def resp(client_with_level_three_roles, webinar: Webinar):
    return client_with_level_three_roles.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}))


def test_logged_user(resp):
    assert resp.status_code == 200


def test_link_unavailable_for_non_users(client):
    resp = client.get(reverse('cohorts:webinar', kwargs={'slug': 'foo'}))
    assert resp.status_code == 302


@pytest.mark.parametrize('property_name', 'speaker speaker_title title description vimeo_id discourse_topic_id'.split())
def test_basic_contents(resp, webinar, property_name):
    dj_assert_contains(resp, getattr(webinar, property_name))


@pytest.fixture
def resp_video_not_recorded(client_with_level_three_roles, webinar: Webinar):
    webinar.vimeo_id = ''
    webinar.save()
    return client_with_level_three_roles.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}))


def test_pending_webinar_msg(resp_video_not_recorded):
    dj_assert_contains(
        resp_video_not_recorded,
        'Ainda não temos máquina do tempo, esse webinário ainda não foi gravado'
    )


def test_vimeo_player_not_present(resp_video_not_recorded):
    dj_assert_not_contains(
        resp_video_not_recorded,
        'src="https://player.vimeo.com/video/"'
    )


@pytest.fixture
def resp_not_level_three(client_with_not_level_three_roles, webinar: Webinar, logged_user):
    return client_with_not_level_three_roles.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}))


def test_webinar_landing_for_client(cohort, resp_not_level_three):
    assert resp_not_level_three.status_code == 302
    assert resp_not_level_three.url == reverse('member_landing_page')
