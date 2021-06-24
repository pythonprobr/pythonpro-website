import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from pythonpro.cohorts.models import Webinar
from pythonpro.cohorts.tests.conftest import img_path
from pythonpro.memberkit.models import Subscription


@pytest.fixture
def webinar(cohort) -> Webinar:
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    return baker.make(Webinar, cohort=cohort, image=image, vimeo_id='1', memberkit_url='https://plataforma.dev.pro.br')


@pytest.fixture
def resp(client_with_user, webinar: Webinar):
    return client_with_user.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}))


def test_logged_user(resp, webinar):
    assert resp.status_code == 302
    assert resp.url == reverse('checkout:bootcamp_lp')


def test_link_unavailable_for_non_users(client):
    resp = client.get(reverse('cohorts:webinar', kwargs={'slug': 'foo'}))
    assert resp.status_code == 302


def test_redirect_user_not_migrated_to_memberkit(client_with_user, webinar, logged_user):
    baker.make(
        Subscription,
        subscriber=logged_user,
        activated_at=None,
        memberkit_user_id=None
    )
    resp = client_with_user.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}))
    assert resp.status_code == 301
    assert resp.url == reverse('migrate_to_memberkit')


def test_python_birds_migrated_user(client_with_user, webinar, logged_user):
    baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=logged_user,
        activated_at=timezone.now(),
        memberkit_user_id=1
    )
    resp = client_with_user.get(reverse('cohorts:webinar', kwargs={'slug': webinar.slug}))
    assert resp.status_code == 301
    assert resp.url == webinar.memberkit_url
