import pytest
from django.urls import reverse

from pythonpro.domain.user_facade import find_user_interactions


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._mailchimp_facade.tag_as')


@pytest.fixture
def launch_status_as_mock(mocker):
    return mocker.patch('pythonpro.launch.views._get_launch_status', return_value=4)


@pytest.fixture
def resp(client, tag_as_mock, launch_status_as_mock):
    return client.get(reverse('launch:cpl3'), secure=True)


def test_status_code(resp):
    assert 200 == resp.status_code


def test_mailchimp_tag_not_called(resp, tag_as_mock):
    assert tag_as_mock.call_count == 0


@pytest.fixture
def resp_with_user(client_with_user, tag_as_mock):
    return client_with_user.get(reverse('launch:cpl3'), secure=True)


def test_user_interaction(resp_with_user, logged_user):
    assert 'CPL3' in [i.category for i in find_user_interactions(logged_user)]


def test_mailchimp_tag(resp_with_user, logged_user, tag_as_mock):
    tag_as_mock.assert_called_once_with(logged_user.email, 'cpl3')
