import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.launch.facade import (
    LAUNCH_STATUS_CPL1,
    LAUNCH_STATUS_CPL2,
    LAUNCH_STATUS_CPL3,
    LAUNCH_STATUS_CPL4
)


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.tag_as.delay')


@pytest.fixture
def resp_on_cpl1_on_air(mocker, client, tag_as_mock):
    mocker.patch('pythonpro.launch.facade.get_launch_status', return_value=LAUNCH_STATUS_CPL1)
    mocker.patch('pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_CPL1)
    return client.get(reverse('launch:cpl1'))


def test_cpl_video_is_present(resp_on_cpl1_on_air):
    dj_assert_contains(resp_on_cpl1_on_air, 'https://www.youtube.com/embed/')


def test_facebook_comments_is_present(resp_on_cpl1_on_air):
    dj_assert_contains(resp_on_cpl1_on_air, 'www.facebook.com/v4.0/plugins/comments.php')


def test_should_return_cpl1_on_air_in_navbar(resp_on_cpl1_on_air):
    dj_assert_contains(resp_on_cpl1_on_air, reverse('launch:cpl1'))


@pytest.fixture
def resp_on_cpl2_on_air(mocker, client, tag_as_mock):
    mocker.patch('pythonpro.launch.facade.get_launch_status', return_value=LAUNCH_STATUS_CPL2)
    mocker.patch('pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_CPL2)
    return client.get(reverse('launch:cpl2'))


def test_should_return_cpl2_on_air_in_navbar(resp_on_cpl2_on_air):
    dj_assert_contains(resp_on_cpl2_on_air, reverse('launch:cpl2'))


@pytest.fixture
def resp_on_cpl3_on_air(mocker, client, tag_as_mock):
    mocker.patch('pythonpro.launch.facade.get_launch_status', return_value=LAUNCH_STATUS_CPL3)
    mocker.patch('pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_CPL3)
    return client.get(reverse('launch:cpl3'))


def test_should_return_cpl3_on_air_in_navbar(resp_on_cpl3_on_air):
    dj_assert_contains(resp_on_cpl3_on_air, reverse('launch:cpl3'))


@pytest.fixture
def resp_on_cpl4_on_air(mocker, client, tag_as_mock):
    mocker.patch('pythonpro.launch.facade.get_launch_status', return_value=LAUNCH_STATUS_CPL4)
    mocker.patch('pythonpro.launch.views.get_launch_status', return_value=LAUNCH_STATUS_CPL4)
    return client.get(reverse('launch:cpl4'))


def test_should_return_cpl4_on_air_in_navbar(resp_on_cpl4_on_air):
    dj_assert_contains(resp_on_cpl4_on_air, reverse('launch:cpl4'))


@pytest.fixture
def resp_cpl_with_debug(mocker, client, tag_as_mock):
    return client.get(reverse('launch:cpl1') + '?debug=1')


def test_should_return_cpl_when_debug_is_true(resp_cpl_with_debug):
    assert resp_cpl_with_debug.status_code == 200
