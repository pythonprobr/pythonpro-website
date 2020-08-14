from datetime import timedelta

import pytest
from django.urls import reverse

from pythonpro.checkout import facade
from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.tag_as.delay')


@pytest.fixture
def resp_no_user_after_discount(client, tag_as_mock, freezer):
    freezer.move_to(facade.discount_35_percent_datetime_limit + timedelta(seconds=1))
    return client.get(reverse('checkout:bootcamp_lp_d3'))


def test_no_user_status_code(resp_no_user_after_discount):
    assert resp_no_user_after_discount.status_code == 200


def test_launch_datetime_finish_on_context(resp_no_user_after_discount):
    assert resp_no_user_after_discount.context['launch_datetime_finish'] == facade.launch_datetime_finish


def test_discount_datetime_on_context(resp_no_user_after_discount):
    assert resp_no_user_after_discount.context['discount_datetime_limit'] == facade.launch_datetime_finish


def test_no_user_no_discount(resp_no_user_after_discount):
    dj_assert_contains(resp_no_user_after_discount, 'R$ 1.997,00')
    assert resp_no_user_after_discount.context['has_first_day_discount'] is False
    assert resp_no_user_after_discount.context['has_client_discount'] is False
    assert resp_no_user_after_discount.context['first_day_discount'] == 0
    assert resp_no_user_after_discount.context['client_discount'] == 0
    assert resp_no_user_after_discount.context['payment_item_config'].slug == 'bootcamp'


@pytest.fixture
def resp_no_user_after_launch_with_debug(client, tag_as_mock, freezer):
    freezer.move_to(facade.launch_datetime_finish + timedelta(seconds=1))
    return client.get(reverse('checkout:bootcamp_lp_d3'), data={'debug': 'true'})


def test_no_user_no_discount_after_launch_with_debug(resp_no_user_after_launch_with_debug):
    dj_assert_contains(resp_no_user_after_launch_with_debug, 'R$ 1.997,00')
    assert resp_no_user_after_launch_with_debug.context['has_first_day_discount'] is False
    assert resp_no_user_after_launch_with_debug.context['has_client_discount'] is False
    assert resp_no_user_after_launch_with_debug.context['first_day_discount'] == 0
    assert resp_no_user_after_launch_with_debug.context['client_discount'] == 0
    assert resp_no_user_after_launch_with_debug.context['payment_item_config'].slug == 'bootcamp'


@pytest.fixture(params=[
    'checkout:bootcamp_lp_d1',
    'checkout:bootcamp_lp_d2',
    'checkout:bootcamp_lp_d3',
    'checkout:bootcamp_lp_d1_webdev',
    'checkout:bootcamp_lp_d2_webdev',
    'checkout:bootcamp_lp_d3_webdev',
])
def resp_debug_all_lp_after_lanch(client_with_lead, tag_as_mock, freezer, request, logged_user):
    freezer.move_to(facade.launch_datetime_finish + timedelta(seconds=1))
    client_with_lead.force_login(logged_user)
    return client_with_lead.get(reverse(request.param), data={'debug': 'true'})


def test_status_code_200_eg_no_redirect(resp_debug_all_lp_after_lanch):
    assert resp_debug_all_lp_after_lanch.status_code == 200


@pytest.fixture
def resp_no_user_with_50_discount(client, tag_as_mock, freezer):
    freezer.move_to(facade.discount_50_percent_datetime_limit - timedelta(seconds=1))
    return client.get(reverse('checkout:bootcamp_lp_d1'))


def test_no_user_with_50_discount(resp_no_user_with_50_discount):
    assert resp_no_user_with_50_discount.context['payment_item_config'].slug == 'bootcamp-50-discount'
    assert resp_no_user_with_50_discount.context['client_discount'] == 0
    assert resp_no_user_with_50_discount.context['first_day_discount'] == 100000
    assert resp_no_user_with_50_discount.context['has_first_day_discount'] is True
    assert resp_no_user_with_50_discount.context['has_client_discount'] is False
    dj_assert_contains(resp_no_user_with_50_discount, 'R$ 99,63')
    discount_video = 'https://www.youtube.com/embed/lIWmM0j-WdM'
    dj_assert_contains(resp_no_user_with_50_discount, discount_video)


@pytest.fixture
def resp_no_user_with_35_discount(client, tag_as_mock, freezer):
    freezer.move_to(facade.discount_35_percent_datetime_limit - timedelta(seconds=1))
    return client.get(reverse('checkout:bootcamp_lp_d2'))


def test_no_user_with_35_discount(resp_no_user_with_35_discount):
    assert resp_no_user_with_35_discount.context['payment_item_config'].slug == 'bootcamp-35-discount'
    assert resp_no_user_with_35_discount.context['client_discount'] == 0
    assert resp_no_user_with_35_discount.context['first_day_discount'] == 70000
    assert resp_no_user_with_35_discount.context['has_first_day_discount'] is True
    assert resp_no_user_with_35_discount.context['has_client_discount'] is False
    dj_assert_contains(resp_no_user_with_35_discount, 'R$ 129,61')
    discount_video = 'https://www.youtube.com/embed/41DjlWEbT1M'
    dj_assert_contains(resp_no_user_with_35_discount, discount_video)


@pytest.fixture
def resp_not_level_two_after_discount(client_with_not_level_one_roles, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_35_percent_datetime_limit + timedelta(seconds=1))
    # freezer for some reason logout user, so must be logged again
    client_with_not_level_one_roles.force_login(logged_user)
    return client_with_not_level_one_roles.get(reverse('checkout:bootcamp_lp_d3'))


def test_tag_as_called(resp_not_level_two_after_discount, logged_user, tag_as_mock):
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, 'potential-member')


def test_not_level_two_ater_discount(resp_not_level_two_after_discount):
    test_no_user_no_discount(resp_not_level_two_after_discount)


def test_not_level_two_with_50_discount(client_with_not_level_one_roles, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_50_percent_datetime_limit - timedelta(seconds=1))
    # freezer for some reason logout user, so must be logged again
    client_with_not_level_one_roles.force_login(logged_user)
    resp = client_with_not_level_one_roles.get(reverse('checkout:bootcamp_lp_d1'))
    test_no_user_with_50_discount(resp)


def test_not_level_two_with_35_discount(client_with_not_level_one_roles, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_35_percent_datetime_limit - timedelta(seconds=1))
    # freezer for some reason logout user, so must be logged again
    client_with_not_level_one_roles.force_login(logged_user)
    resp = client_with_not_level_one_roles.get(reverse('checkout:bootcamp_lp_d2'))
    test_no_user_with_35_discount(resp)


def test_webdev_after_discount(client_with_webdev, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_35_percent_datetime_limit + timedelta(seconds=1))
    client_with_webdev.force_login(logged_user)  # freezer for some reason logout user, so must be logged again
    resp = client_with_webdev.get(reverse('checkout:bootcamp_lp_d3_webdev'))
    assert resp.context['payment_item_config'].slug == 'bootcamp-webdev'
    assert resp.context['client_discount'] == 49700
    assert resp.context['first_day_discount'] == 0
    assert resp.context['has_first_day_discount'] is False
    assert resp.context['has_client_discount'] is True
    no_discount_video = 'https://www.youtube.com/embed/rwxY_WjIjEE'
    dj_assert_contains(resp, no_discount_video)
    dj_assert_contains(resp, 'R$ 199,56')


def test_webdev_with_50_discount(client_with_webdev, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_50_percent_datetime_limit - timedelta(seconds=1))
    client_with_webdev.force_login(logged_user)  # freezer for some reason logout user, so must be logged again
    resp = client_with_webdev.get(reverse('checkout:bootcamp_lp_d1_webdev'))
    assert resp.context['payment_item_config'].slug == 'bootcamp-webdev-50-discount'
    assert resp.context['client_discount'] == 49700
    assert resp.context['first_day_discount'] == 100000
    assert resp.context['has_first_day_discount'] is True
    assert resp.context['has_client_discount'] is True
    dj_assert_contains(resp, 'R$ 49,96')


def test_webdev_with_35_discount(client_with_webdev, logged_user, tag_as_mock, freezer):
    freezer.move_to(facade.discount_35_percent_datetime_limit - timedelta(seconds=1))
    client_with_webdev.force_login(logged_user)  # freezer for some reason logout user, so must be logged again
    resp = client_with_webdev.get(reverse('checkout:bootcamp_lp_d2_webdev'))
    assert resp.context['payment_item_config'].slug == 'bootcamp-webdev-35-discount'
    assert resp.context['client_discount'] == 49700
    assert resp.context['first_day_discount'] == 70000
    assert resp.context['has_first_day_discount'] is True
    assert resp.context['has_client_discount'] is True
    dj_assert_contains(resp, 'R$ 79,94')
