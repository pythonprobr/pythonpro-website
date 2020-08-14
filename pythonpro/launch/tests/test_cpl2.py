import pytest
from django.urls import reverse

from pythonpro.domain.user_domain import find_user_interactions
from pythonpro.launch.facade import LAUNCH_STATUS_OPEN_CART, LAUNCH_STATUS_CPL2


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.tag_as.delay')


@pytest.fixture
def launch_status_as_mock(mocker):
    return mocker.patch(
        'pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_OPEN_CART
    )


@pytest.fixture
def resp(client, tag_as_mock, launch_status_as_mock):
    return client.get(reverse('launch:cpl2'))


def test_status_code(resp):
    assert 302 == resp.status_code


def test_email_marketing_tag_not_called(resp, tag_as_mock):
    assert tag_as_mock.call_count == 0


@pytest.fixture
def resp_with_user(client_with_user, tag_as_mock):
    return client_with_user.get(reverse('launch:cpl2'))


def test_user_interaction(resp_with_user, logged_user):
    assert 'CPL2' in [i.category for i in find_user_interactions(logged_user)]


def test_email_marketing_tag(resp_with_user, logged_user, tag_as_mock):
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, 'cpl2')


@pytest.fixture
def launch_status_as_mock_open(mocker):
    return mocker.patch(
        'pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_CPL2
    )


@pytest.fixture
def resp_open(client, tag_as_mock, launch_status_as_mock_open):
    return client.get(reverse('launch:cpl2'))


def test_open_status_code(resp_open):
    assert 200 == resp_open.status_code
