import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_mommy import mommy

from pythonpro.cohorts.models import Webinar
from pythonpro.cohorts.tests.conftest import img_path
from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def webinar(cohort) -> Webinar:
    image = SimpleUploadedFile(name='renzo-nuccitelli.png', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    return mommy.make(Webinar, cohort=cohort, image=image)


@pytest.fixture
def resp(client_with_user, webinar: Webinar):
    return client_with_user.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}), secure=True)


def test_logged_user(resp):
    assert resp.status_code == 200


def test_link_unavailable_for_non_users(client):
    resp = client.get(reverse('cohorts:webinar', kwargs={'slug': 'foo'}), secure=True)
    assert resp.status_code == 302


@pytest.mark.parametrize('property_name', 'speaker speaker_title title description vimeo_id discourse_topic_id'.split())
def test_basic_contents(resp, webinar, property_name):
    dj_assert_contains(resp, getattr(webinar, property_name))
