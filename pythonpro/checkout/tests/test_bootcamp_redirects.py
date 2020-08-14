from datetime import timedelta

import pytest
from django.urls import reverse

from pythonpro.checkout import facade


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.tag_as.delay')


def assert_redirect_with_querystring(client, from_path, tag_as_mock, to_path):
    qs = '?utm_source=google'
    resp = client.get(reverse(from_path) + qs)
    assert resp.status_code == 302
    assert resp.url == reverse(to_path) + qs
    assert not tag_as_mock.called


lp_redirects_rules = pytest.mark.parametrize(
    'from_path, to_path, expire_date',
    [
        ('checkout:bootcamp_lp', 'checkout:bootcamp_lp_d1', facade.launch_datetime_begin),
        ('checkout:bootcamp_lp_d2', 'checkout:bootcamp_lp_d1', facade.launch_datetime_begin),
        ('checkout:bootcamp_lp_d3', 'checkout:bootcamp_lp_d1', facade.launch_datetime_begin),
        ('checkout:bootcamp_lp', 'checkout:bootcamp_lp_d1', facade.discount_50_percent_datetime_limit),
        ('checkout:bootcamp_lp_d2', 'checkout:bootcamp_lp_d1', facade.discount_50_percent_datetime_limit),
        ('checkout:bootcamp_lp_d3', 'checkout:bootcamp_lp_d1', facade.discount_50_percent_datetime_limit),
        (
            'checkout:bootcamp_lp', 'checkout:bootcamp_lp_d2',
            facade.discount_50_percent_datetime_limit + timedelta(seconds=1)),
        (
            'checkout:bootcamp_lp_d1', 'checkout:bootcamp_lp_d2',
            facade.discount_50_percent_datetime_limit + timedelta(seconds=1)),
        (
            'checkout:bootcamp_lp_d3', 'checkout:bootcamp_lp_d2',
            facade.discount_50_percent_datetime_limit + timedelta(seconds=1)),
        ('checkout:bootcamp_lp', 'checkout:bootcamp_lp_d2', facade.discount_35_percent_datetime_limit),
        ('checkout:bootcamp_lp_d1', 'checkout:bootcamp_lp_d2', facade.discount_35_percent_datetime_limit),
        ('checkout:bootcamp_lp_d3', 'checkout:bootcamp_lp_d2', facade.discount_35_percent_datetime_limit),
        (
            'checkout:bootcamp_lp', 'checkout:bootcamp_lp_d3',
            facade.discount_35_percent_datetime_limit + timedelta(seconds=1)),
        (
            'checkout:bootcamp_lp_d1', 'checkout:bootcamp_lp_d3',
            facade.discount_35_percent_datetime_limit + timedelta(seconds=1)),
        (
            'checkout:bootcamp_lp_d2', 'checkout:bootcamp_lp_d3',
            facade.discount_35_percent_datetime_limit + timedelta(seconds=1)),
        ('checkout:bootcamp_lp', 'checkout:bootcamp_lp_d3', facade.launch_datetime_finish),
        ('checkout:bootcamp_lp_d1', 'checkout:bootcamp_lp_d3', facade.launch_datetime_finish),
        ('checkout:bootcamp_lp_d2', 'checkout:bootcamp_lp_d3', facade.launch_datetime_finish),
        (
            'checkout:bootcamp_lp_d3', 'checkout:bootcamp_lp', facade.launch_datetime_finish + timedelta(seconds=1)
        ),
        (
            'checkout:bootcamp_lp_d1', 'checkout:bootcamp_lp', facade.launch_datetime_finish + timedelta(seconds=1)
        ),
        (
            'checkout:bootcamp_lp_d2', 'checkout:bootcamp_lp', facade.launch_datetime_finish + timedelta(seconds=1)
        ),
        (
            'checkout:bootcamp_lp_d3', 'checkout:bootcamp_lp', facade.launch_datetime_begin - timedelta(seconds=1)
        ),
        (
            'checkout:bootcamp_lp_d1', 'checkout:bootcamp_lp', facade.launch_datetime_begin - timedelta(seconds=1)
        ),
        (
            'checkout:bootcamp_lp_d2', 'checkout:bootcamp_lp', facade.launch_datetime_begin - timedelta(seconds=1)
        ),
    ]
)


@lp_redirects_rules
def test_no_user(from_path, to_path, expire_date, client, tag_as_mock, freezer):
    freezer.move_to(expire_date)
    assert_redirect_with_querystring(client, from_path, tag_as_mock, to_path)


@lp_redirects_rules
def test_no_level_two_users(from_path, to_path, expire_date, client_with_not_level_two_roles, tag_as_mock, freezer):
    freezer.move_to(expire_date)
    assert_redirect_with_querystring(client_with_not_level_two_roles, from_path, tag_as_mock, to_path)


@lp_redirects_rules
def test_webev_discount(from_path, to_path, expire_date, client_with_webdev, tag_as_mock, freezer, logged_user):
    freezer.move_to(expire_date)
    # freezer for some reason logout user, so must be logged again
    client_with_webdev.force_login(logged_user)
    if to_path != 'checkout:bootcamp_lp':
        to_path = f'{to_path}_webdev'
    assert_redirect_with_querystring(client_with_webdev, from_path, tag_as_mock, to_path)


@pytest.mark.parametrize(
    'from_path, to_path, expire_date',
    [
        ('checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d1', facade.launch_datetime_begin),
        ('checkout:bootcamp_lp_d2_webdev', 'checkout:bootcamp_lp_d1', facade.launch_datetime_begin),
        ('checkout:bootcamp_lp_d3_webdev', 'checkout:bootcamp_lp_d1', facade.launch_datetime_begin),
        ('checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d1', facade.discount_50_percent_datetime_limit),
        ('checkout:bootcamp_lp_d2_webdev', 'checkout:bootcamp_lp_d1', facade.discount_50_percent_datetime_limit),
        ('checkout:bootcamp_lp_d3_webdev', 'checkout:bootcamp_lp_d1', facade.discount_50_percent_datetime_limit),
        (
                'checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d2',
                facade.discount_50_percent_datetime_limit + timedelta(seconds=1)),
        (
                'checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d2',
                facade.discount_50_percent_datetime_limit + timedelta(seconds=1)),
        (
                'checkout:bootcamp_lp_d3_webdev', 'checkout:bootcamp_lp_d2',
                facade.discount_50_percent_datetime_limit + timedelta(seconds=1)),
        ('checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d2', facade.discount_35_percent_datetime_limit),
        ('checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d2', facade.discount_35_percent_datetime_limit),
        ('checkout:bootcamp_lp_d3_webdev', 'checkout:bootcamp_lp_d2', facade.discount_35_percent_datetime_limit),
        (
                'checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d3',
                facade.discount_35_percent_datetime_limit + timedelta(seconds=1)),
        (
                'checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d3',
                facade.discount_35_percent_datetime_limit + timedelta(seconds=1)),
        (
                'checkout:bootcamp_lp_d2_webdev', 'checkout:bootcamp_lp_d3',
                facade.discount_35_percent_datetime_limit + timedelta(seconds=1)),
        ('checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d3', facade.launch_datetime_finish),
        ('checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp_d3', facade.launch_datetime_finish),
        ('checkout:bootcamp_lp_d2_webdev', 'checkout:bootcamp_lp_d3', facade.launch_datetime_finish),
        (
                'checkout:bootcamp_lp_d3_webdev', 'checkout:bootcamp_lp',
                facade.launch_datetime_finish + timedelta(seconds=1)
        ),
        (
                'checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp',
                facade.launch_datetime_finish + timedelta(seconds=1)
        ),
        (
                'checkout:bootcamp_lp_d2_webdev', 'checkout:bootcamp_lp',
                facade.launch_datetime_finish + timedelta(seconds=1)
        ),
        (
                'checkout:bootcamp_lp_d3_webdev', 'checkout:bootcamp_lp',
                facade.launch_datetime_begin - timedelta(seconds=1)
        ),
        (
                'checkout:bootcamp_lp_d1_webdev', 'checkout:bootcamp_lp',
                facade.launch_datetime_begin - timedelta(seconds=1)
        ),
        (
                'checkout:bootcamp_lp_d2_webdev', 'checkout:bootcamp_lp',
                facade.launch_datetime_begin - timedelta(seconds=1)
        ),
    ]
)
def test_not_webev_trying_access_discount(
        from_path, to_path, expire_date, client_with_not_level_two_roles, tag_as_mock, freezer, logged_user):
    freezer.move_to(expire_date)
    # freezer for some reason logout user, so must be logged again
    client_with_not_level_two_roles.force_login(logged_user)
    assert_redirect_with_querystring(client_with_not_level_two_roles, from_path, tag_as_mock, to_path)
