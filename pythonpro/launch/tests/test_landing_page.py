import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.domain.user_domain import find_user_interactions
from pythonpro.launch.facade import (
    LAUNCH_STATUS_CPL1,
    LAUNCH_STATUS_CPL2,
    LAUNCH_STATUS_CPL3,
    LAUNCH_STATUS_CPL4,
    LAUNCH_STATUS_PPL,
    LAUNCH_STATUS_OPEN_CART,
    LAUNCH_STATUS_CLOSED
)


@pytest.fixture
def resp(client, mocker):
    mocker.patch('pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_PPL)
    return client.get(reverse('launch:landing_page'))


def test_status_code(resp):
    assert 200 == resp.status_code


def test_email_field_is_present(resp):
    dj_assert_contains(resp, 'type="email" name="email"')


def test_submmit_button_is_present(resp):
    dj_assert_contains(resp, 'type="submit"')


def test_form_action_is_present(resp):
    dj_assert_contains(resp, f'action="{reverse("launch:lead_form")}" method="POST"')


@pytest.fixture
def resp_with_user(mocker, client_with_user):
    mocker.patch('pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_PPL)
    return client_with_user.get(reverse('launch:landing_page'))


def test_user_interaction(resp_with_user, logged_user):
    assert 'LAUNCH_LP' in [i.category for i in find_user_interactions(logged_user)]


@pytest.mark.parametrize(
    'status',
    [
        LAUNCH_STATUS_CPL1,
        LAUNCH_STATUS_CPL2,
        LAUNCH_STATUS_CPL3,
        LAUNCH_STATUS_CPL4,
    ]
)
def test_status_code_should_return_200_when_cpl(mocker, client, status):
    mocker.patch('pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_CPL1)
    resp = client.get(reverse('launch:landing_page'), follow=False)
    assert 200 == resp.status_code


def test_status_code_should_return_302_when_open_cart(mocker, client):
    mocker.patch('pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_OPEN_CART)
    resp = client.get(reverse('launch:landing_page'), follow=False)
    assert 302 == resp.status_code


def test_status_code_should_return_200_when_close_cart(mocker, client):
    mocker.patch('pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_CLOSED)
    resp = client.get(reverse('launch:landing_page'), follow=False)
    assert 200 == resp.status_code
