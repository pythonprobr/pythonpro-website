from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from pythonpro.cohorts.models import LiveClass
from pythonpro.memberkit.models import Subscription


@pytest.fixture
def live_class(db, cohort, fake) -> LiveClass:
    now = timezone.now()
    return baker.make(
        LiveClass,
        cohort=cohort,
        vimeo_id='1212',
        start=now + timedelta(days=1),
        description=fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None),
        memberkit_url='https://plataforma.dev.pro.br'
    )


@pytest.fixture
def resp(client_with_user, live_class: LiveClass):
    return client_with_user.get(reverse('cohorts:live_class', kwargs={'pk': live_class.id}))


def test_logged_user(resp):
    assert resp.status_code == 302
    assert resp.url == reverse('checkout:bootcamp_lp')


def test_link_unavailable_for_non_users(client):
    resp = client.get(reverse('cohorts:live_class', kwargs={'pk': 1}))
    assert resp.status_code == 302


def test_redirect_user_not_migrated_to_memberkit(client_with_user, live_class, logged_user):
    baker.make(
        Subscription,
        subscriber=logged_user,
        activated_at=None,
        memberkit_user_id=None
    )
    resp = client_with_user.get(reverse('cohorts:live_class', kwargs={'pk': live_class.id}))
    assert resp.status_code == 301
    assert resp.url == reverse('migrate_to_memberkit')


def test_redirect_user_migrated_to_memberkit(client_with_user, live_class, logged_user):
    baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=logged_user,
        activated_at=timezone.now(),
        memberkit_user_id=1
    )
    resp = client_with_user.get(reverse('cohorts:live_class', kwargs={'pk': live_class.id}))
    assert resp.status_code == 301
    assert resp.url == live_class.memberkit_url
