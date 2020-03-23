import pytest
from django.urls import reverse


@pytest.fixture
def resp(client):
    return client.get(reverse('checkout:pytools_lp'), secure=True)


def test_status_code(resp):
    assert resp.status_code == 200


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as.delay')


@pytest.fixture
def resp_with_user(client_with_user, tag_as_mock, logged_user):
    return client_with_user.get(reverse('checkout:pytools_lp'), secure=True)


def test_logged_user_status_code(resp_with_user):
    assert resp_with_user.status_code == 200


def test_tagging(resp_with_user, tag_as_mock, logged_user):
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, 'potential-client')
