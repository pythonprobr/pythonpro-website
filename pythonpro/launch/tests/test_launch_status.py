from datetime import datetime

import pytest

from django.urls import reverse
from django.utils import timezone

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.launch.views import (
    _get_launch_status,
    LAUNCH_STATUS_CPL1,
    LAUNCH_STATUS_CPL2,
    LAUNCH_STATUS_CPL3,
    LAUNCH_STATUS_PPL,
    LAUNCH_STATUS_OPEN_CART,
)


def test_should_return_launch_status_ppl_before_monday(mocker):
    date = timezone.make_aware(datetime(2019, 10, 27))
    mocker.patch('pythonpro.launch.views.timezone.now', return_value=date)
    assert _get_launch_status() == LAUNCH_STATUS_PPL


def test_should_return_launch_status_cpl1_on_monday(mocker):
    date = timezone.make_aware(datetime(2019, 10, 28))
    mocker.patch('pythonpro.launch.views.timezone.now', return_value=date)
    assert _get_launch_status() == LAUNCH_STATUS_CPL1


def test_should_return_launch_status_cpl1_on_tuesday(mocker):
    date = timezone.make_aware(datetime(2019, 10, 29))
    mocker.patch('pythonpro.launch.views.timezone.now', return_value=date)
    assert _get_launch_status() == LAUNCH_STATUS_CPL1


def test_should_return_launch_status_cpl2_on_wednesday(mocker):
    date = timezone.make_aware(datetime(2019, 10, 30))
    mocker.patch('pythonpro.launch.views.timezone.now', return_value=date)
    assert _get_launch_status() == LAUNCH_STATUS_CPL2


def test_should_return_launch_status_cpl2_on_thursday(mocker):
    date = timezone.make_aware(datetime(2019, 10, 31))
    mocker.patch('pythonpro.launch.views.timezone.now', return_value=date)
    assert _get_launch_status() == LAUNCH_STATUS_CPL2


def test_should_return_launch_status_cpl3_on_friday(mocker):
    date = timezone.make_aware(datetime(2019, 11, 1))
    mocker.patch('pythonpro.launch.views.timezone.now', return_value=date)
    assert _get_launch_status() == LAUNCH_STATUS_CPL3


def test_should_return_launch_status_cpl3_on_saturday(mocker):
    date = timezone.make_aware(datetime(2019, 11, 2))
    mocker.patch('pythonpro.launch.views.timezone.now', return_value=date)
    assert _get_launch_status() == LAUNCH_STATUS_CPL3


def test_should_return_launch_status_cpl3_on_sunday(mocker):
    date = timezone.make_aware(datetime(2019, 11, 3))
    mocker.patch('pythonpro.launch.views.timezone.now', return_value=date)
    assert _get_launch_status() == LAUNCH_STATUS_CPL3


def test_should_return_launch_status_open_cart_on_next_monday(mocker):
    date = timezone.make_aware(datetime(2019, 11, 4))
    mocker.patch('pythonpro.launch.views.timezone.now', return_value=date)
    assert _get_launch_status() == LAUNCH_STATUS_OPEN_CART


@pytest.fixture
def status_ppl(mocker):
    return mocker.patch('pythonpro.launch.views._get_launch_status', return_value=0)


def test_should_cpl1_redirect_to_landing_page(client, status_ppl):
    response = client.get(reverse('launch:cpl1'), secure=True, redirect=False)
    assert response.status_code == 302


def test_should_cpl2_redirect_to_landing_page(client, status_ppl):
    response = client.get(reverse('launch:cpl2'), secure=True, redirect=False)
    assert response.status_code == 302


def test_should_cpl3_redirect_to_landing_page(client, status_ppl):
    response = client.get(reverse('launch:cpl3'), secure=True, redirect=False)
    assert response.status_code == 302


def test_should_not_redirect_to_landing_page_when_param_debug_was_setted(client, status_ppl):
    response = client.get(reverse('launch:cpl1') + '?debug=1', secure=True, redirect=False)
    assert response.status_code == 200




@pytest.fixture
def status_cpl1(mocker):
    return mocker.patch('pythonpro.launch.views._get_launch_status', return_value=1)


@pytest.fixture
def response_as_status_cpl1(mocker, status_cpl1, client):
    return client.get(reverse('launch:cpl1'), secure=True)


def test_should_show_video1_as_available_on_status_cpl1(response_as_status_cpl1):
    dj_assert_contains(response_as_status_cpl1, 'video1-available.png')


def test_should_show_video2_as_unavailable_on_status_cpl1(response_as_status_cpl1):
    dj_assert_contains(response_as_status_cpl1, 'video2-unavailable.png')


def test_should_show_video3_as_unavailable_on_status_cpl1(response_as_status_cpl1):
    dj_assert_contains(response_as_status_cpl1, 'video3-unavailable.png')


@pytest.fixture
def status_cpl2(mocker):
    return mocker.patch('pythonpro.launch.views._get_launch_status', return_value=2)


@pytest.fixture
def response_as_status_cpl2(mocker, status_cpl2, client):
    return client.get(reverse('launch:cpl1'), secure=True)


def test_should_show_video1_as_available_on_status_cpl2(response_as_status_cpl2):
    dj_assert_contains(response_as_status_cpl2, 'video1-available.png')


def test_should_show_video2_as_available_on_status_cpl2(response_as_status_cpl2):
    dj_assert_contains(response_as_status_cpl2, 'video2-available.png')


def test_should_show_video3_as_unavailable_on_status_cpl2(response_as_status_cpl2):
    dj_assert_contains(response_as_status_cpl2, 'video3-unavailable.png')


@pytest.fixture
def status_cpl3(mocker):
    return mocker.patch('pythonpro.launch.views._get_launch_status', return_value=3)


@pytest.fixture
def response_as_status_cpl3(mocker, status_cpl3, client):
    return client.get(reverse('launch:cpl1'), secure=True)


def test_should_show_video1_as_available_on_status_cpl3(response_as_status_cpl3):
    dj_assert_contains(response_as_status_cpl3, 'video1-available.png')


def test_should_show_video2_as_available_on_status_cpl3(response_as_status_cpl3):
    dj_assert_contains(response_as_status_cpl3, 'video2-available.png')


def test_should_show_video3_as_available_on_status_cpl3(response_as_status_cpl3):
    dj_assert_contains(response_as_status_cpl3, 'video3-available.png')
