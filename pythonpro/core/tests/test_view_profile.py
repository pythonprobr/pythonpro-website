import pytest
from django.test import Client
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def resp(client: Client):
    return client.get(reverse('core:profile'), secure=True)


@pytest.fixture
def user(django_user_model):
    usr = mommy.make(django_user_model)
    return usr


@pytest.fixture
def resp_with_user(user, client: Client):
    client.force_login(user)
    return resp(client)


def test_profile_not_logged_user(resp):
    assert 302 == resp.status_code


def test_profile_status_code(resp_with_user):
    assert 200 == resp_with_user.status_code


def test_profile_first_name(user, resp_with_user):
    dj_assert_contains(resp_with_user, user.first_name)


def test_profile_email(user, resp_with_user):
    dj_assert_contains(resp_with_user, user.email)


def test_edit_name_link(resp_with_user):
    dj_assert_contains(resp_with_user, reverse('core:profile_name'))


def test_edit_email_link(resp_with_user):
    dj_assert_contains(resp_with_user, reverse('core:profile_email'))


'''Add password validation on user profile screen'''


def test_edit_password_link(resp_with_user):
    dj_assert_contains(resp_with_user, reverse('core:profile_password'))
