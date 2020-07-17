from datetime import timedelta

import pytest
from django.urls import reverse

from pythonpro.checkout import facade
from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as.delay')


@pytest.fixture
def resp(client, tag_as_mock, freezer, logged_user):
    freezer.move_to(facade.launch_datetime_finish + timedelta(seconds=1))
    client.force_login(logged_user)
    return client.get(reverse('checkout:membership_lp'))


def test_tag_as_called(resp, logged_user, tag_as_mock):
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, 'potential-member')


def test_status_code(resp):
    assert resp.status_code == 200


def test_subscription_link_is_present(resp):
    dj_assert_contains(resp, reverse('checkout:membership_lp'))


@pytest.fixture
def resp_no_user(client, freezer):
    freezer.move_to(facade.launch_datetime_finish + timedelta(seconds=1))
    resp = client.get(reverse('checkout:membership_lp'))
    return resp


def test_no_user_status_code(resp_no_user):
    assert resp_no_user.status_code == 200


def test_no_tagging(resp_no_user, tag_as_mock):
    assert tag_as_mock.call_count == 0
