import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.domain.user_domain import find_user_interactions


@pytest.fixture
def resp(client, cohort):
    return client.get(reverse('launch:ty'))


def test_status_code(resp):
    assert 200 == resp.status_code


@pytest.mark.parametrize(
    'media_link',
    [
        'https://twitter.com/renzoprobr',
        'https://www.youtube.com/user/renzonuccitelli',
        'https://instagram.com/renzoprobr',
    ]

)
def test_email_field_is_present(resp, media_link):
    dj_assert_contains(resp, media_link)


@pytest.fixture
def resp_with_user(client_with_user, cohort):
    return client_with_user.get(reverse('launch:ty'))


def test_user_interaction(resp_with_user, logged_user):
    assert 'LAUNCH_SUBSCRIPTION' in [i.category for i in find_user_interactions(logged_user)]
