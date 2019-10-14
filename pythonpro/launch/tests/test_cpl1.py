import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.domain.user_facade import find_user_interactions


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._mailchimp_facade.tag_as')


@pytest.fixture
def resp(client, tag_as_mock):
    return client.get(reverse('launch:cpl1'), secure=True)


def test_status_code(resp):
    assert 200 == resp.status_code


def test_mailchimp_tag_not_called(resp, tag_as_mock):
    assert tag_as_mock.call_count == 0


def test_cpl_video_is_present(resp):
    dj_assert_contains(resp, 'https://www.youtube.com/embed/')


def test_facebook_comments_is_present(resp):
    dj_assert_contains(resp, f'<div class="fb-comment-embed" data-href="https://localhost{reverse("launch:cpl1")}')


@pytest.fixture
def resp_with_user(client_with_user, tag_as_mock):
    return client_with_user.get(reverse('launch:cpl1'), secure=True)


def test_user_interaction(resp_with_user, logged_user):
    assert 'CPL1' in [i.category for i in find_user_interactions(logged_user)]


def test_mailchimp_tag(resp_with_user, logged_user, tag_as_mock):
    tag_as_mock.assert_called_once_with(logged_user.email, 'cpl1')
