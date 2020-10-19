from datetime import timedelta

import pytest
from django.urls import reverse

from pythonpro.checkout import facade
from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.tag_as.delay')


@pytest.fixture
def visit_member_landing_page_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._core_facade.visit_member_landing_page')


@pytest.fixture
def subscribe_to_waiting_list_mock(mocker):
    return mocker.patch('pythonpro.checkout.views.user_domain.subscribe_to_waiting_list')


begin_and_finish = [
    facade.launch_datetime_finish + timedelta(seconds=1),  # after finish
    facade.launch_datetime_begin - timedelta(seconds=1),  # before begin
]
after_and_before_launch = pytest.fixture(params=begin_and_finish)


@after_and_before_launch
def resp(client, tag_as_mock, freezer, logged_user, request, visit_member_landing_page_mock):
    freezer.move_to(request.param)
    client.force_login(logged_user)
    return client.get(reverse('checkout:bootcamp_lp') + '?utm_source=google')


def test_tag_as_called(resp, logged_user, tag_as_mock):
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, 'potential-member')


def test_status_code(resp):
    assert resp.status_code == 200


def test_subscription_link_is_present(resp):
    dj_assert_contains(resp, reverse('checkout:bootcamp_lp'))


def test_user_visited_bootcamp_lp(resp, logged_user, visit_member_landing_page_mock):
    visit_member_landing_page_mock.assert_called_once_with(logged_user, 'google')


@after_and_before_launch
def resp_no_user(client, freezer, request, tag_as_mock):
    freezer.move_to(request.param)
    return client.get(reverse('checkout:bootcamp_lp'))


def test_no_user_status_code(resp_no_user):
    assert resp_no_user.status_code == 200


def test_no_tagging(resp_no_user, tag_as_mock):
    assert tag_as_mock.call_count == 0


@pytest.mark.parametrize('dt', begin_and_finish)
def test_post_with_user(dt, client, freezer, subscribe_to_waiting_list_mock, logged_user):
    freezer.move_to(dt)
    client.force_login(logged_user)
    resp_with_user = client.post(
        reverse('checkout:bootcamp_lp') + '?utm_source=google',
        data={'email': 'jhon@email.com', 'first_name': 'Jhon', 'phone': '+5512999999999'}
    )
    subscribe_to_waiting_list_mock.assert_called_once_with(
        resp_with_user.cookies['sessionid'].value,
        logged_user,
        '+5512999999999',
        'google')


@pytest.fixture
def subscribe_anonymous_user_to_waiting_list_mock(mocker):
    return mocker.patch('pythonpro.checkout.views.user_domain.subscribe_anonymous_user_to_waiting_list')


@pytest.mark.parametrize('dt', begin_and_finish)
def test_post_absent_user(dt, client, freezer, subscribe_anonymous_user_to_waiting_list_mock):
    freezer.move_to(dt)
    client.post(
        reverse('checkout:bootcamp_lp') + '?utm_source=google',
        data={'email': 'jhon@email.com', 'first_name': 'Jhon', 'phone': '+5512999999999'}
    )
    subscribe_anonymous_user_to_waiting_list_mock.assert_called_once_with(
        None, 'jhon@email.com', 'Jhon', '+5512999999999', 'google')
