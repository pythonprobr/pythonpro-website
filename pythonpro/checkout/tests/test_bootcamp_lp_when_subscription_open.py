from datetime import timedelta

import pytest
from django.urls import reverse

from pythonpro.checkout import facade
from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as.delay')


@pytest.fixture
def resp_no_user_after_discount(client, tag_as_mock, freezer):
    freezer.move_to(facade.discount_datetime_limit + timedelta(seconds=1))
    return client.get(reverse('checkout:bootcamp_lp'))


def test_no_user_status_code(resp_no_user_after_discount):
    assert resp_no_user_after_discount.status_code == 200


def test_launch_datetime_finish_on_context(resp_no_user_after_discount):
    assert resp_no_user_after_discount.context['launch_datetime_finish'] == facade.launch_datetime_finish


def test_discount_datetime_on_context(resp_no_user_after_discount):
    assert resp_no_user_after_discount.context['discount_datetime_limit'] == facade.discount_datetime_limit


def test_no_user_no_discount(resp_no_user_after_discount):
    dj_assert_contains(resp_no_user_after_discount, 'R$ 1.997,00')
    assert resp_no_user_after_discount.context['has_first_day_discount'] is False
    assert resp_no_user_after_discount.context['has_client_discount'] is False
    assert resp_no_user_after_discount.context['first_day_discount'] == 0
    assert resp_no_user_after_discount.context['client_discount'] == 0
    assert resp_no_user_after_discount.context['payment_item_config'].slug == 'membership'


@pytest.fixture
def resp_no_user_before_discount(client, tag_as_mock, freezer):
    freezer.move_to(facade.discount_datetime_limit - timedelta(seconds=1))
    return client.get(reverse('checkout:bootcamp_lp'))


def test_no_user_with_first_day_discount(resp_no_user_before_discount):
    assert resp_no_user_before_discount.context['payment_item_config'].slug == 'membership-first-day'
    assert resp_no_user_before_discount.context['client_discount'] == 0
    assert resp_no_user_before_discount.context['first_day_discount'] == 40000
    assert resp_no_user_before_discount.context['has_first_day_discount'] is True
    assert resp_no_user_before_discount.context['has_client_discount'] is False
    dj_assert_contains(resp_no_user_before_discount, 'R$ 159,59')
    discount_video = 'https://www.youtube.com/embed/0rzm6NjyoSw'
    dj_assert_contains(resp_no_user_before_discount, discount_video)


@pytest.fixture
def resp_with_lead_after_discount(client_with_lead, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_datetime_limit + timedelta(seconds=1))
    client_with_lead.force_login(logged_user)  # freezer for some reason logout user, so must be logged again
    return client_with_lead.get(reverse('checkout:bootcamp_lp'))


def test_tag_as_called(resp_with_lead_after_discount, logged_user, tag_as_mock):
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, 'potential-member')


def test_lead_without_discount(resp_with_lead_after_discount):
    test_no_user_no_discount(resp_with_lead_after_discount)


def test_lead_with_first_day_discount(client_with_lead, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_datetime_limit - timedelta(seconds=1))
    client_with_lead.force_login(logged_user)  # freezer for some reason logout user, so must be logged again
    resp = client_with_lead.get(reverse('checkout:bootcamp_lp'))
    test_no_user_with_first_day_discount(resp)


def test_client_without_first_day_discount(client_with_client, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_datetime_limit + timedelta(seconds=1))
    client_with_client.force_login(logged_user)  # freezer for some reason logout user, so must be logged again
    resp = client_with_client.get(reverse('checkout:bootcamp_lp'))
    assert resp.context['payment_item_config'].slug == 'membership-client'
    assert resp.context['client_discount'] == 10000
    assert resp.context['first_day_discount'] == 0
    assert resp.context['has_first_day_discount'] is False
    assert resp.context['has_client_discount'] is True
    no_discount_video = 'https://www.youtube.com/embed/g-C_5oUCz2A'
    dj_assert_contains(resp, no_discount_video)
    dj_assert_contains(resp, 'R$ 189,57')


def test_client_with_first_day_discount(client_with_client, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_datetime_limit - timedelta(seconds=1))
    client_with_client.force_login(logged_user)  # freezer for some reason logout user, so must be logged again
    resp = client_with_client.get(reverse('checkout:bootcamp_lp'))
    assert resp.context['payment_item_config'].slug == 'membership-client-first-day'
    assert resp.context['client_discount'] == 10000
    assert resp.context['first_day_discount'] == 40000
    assert resp.context['has_first_day_discount'] is True
    assert resp.context['has_client_discount'] is True
    dj_assert_contains(resp, 'R$ 149,60')
