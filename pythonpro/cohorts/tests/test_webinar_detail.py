import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_mommy import mommy

from pythonpro.cohorts.models import Webinar
from pythonpro.cohorts.tests.conftest import img_path
from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains


@pytest.fixture
def webinar(cohort) -> Webinar:
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    return mommy.make(Webinar, cohort=cohort, image=image, vimeo_id='1')


@pytest.fixture
def resp(client_with_member, webinar: Webinar):
    return client_with_member.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}), secure=True)


def test_logged_user(resp):
    assert resp.status_code == 200


def test_link_unavailable_for_non_users(client):
    resp = client.get(reverse('cohorts:webinar', kwargs={'slug': 'foo'}), secure=True)
    assert resp.status_code == 302


@pytest.mark.parametrize('property_name', 'speaker speaker_title title description vimeo_id discourse_topic_id'.split())
def test_basic_contents(resp, webinar, property_name):
    dj_assert_contains(resp, getattr(webinar, property_name))


@pytest.fixture
def resp_video_not_recorded(client_with_member, webinar: Webinar):
    webinar.vimeo_id = ''
    webinar.save()
    return client_with_member.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}), secure=True)


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
def resp_client(client_with_client, webinar: Webinar, mocker, logged_user):
    return client_with_client.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}), secure=True)


def test_webinar_landing_for_client(cohort, resp_client):
    assert resp_client.status_code == 302
    assert resp_client.url == reverse('member_landing_page')


@pytest.fixture
def resp_lead(client_with_lead, webinar: Webinar, mocker, logged_user):
    return client_with_lead.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}), secure=True)


def test_webinar_landing_for_lead(cohort, resp_lead):
    assert resp_lead.status_code == 302
    assert resp_lead.url == reverse('member_landing_page')
