import pytest
from django.test import Client
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def resp(client: Client):
    return _resp(client)


def _resp(client):
    """Plain function to avoid _pytest.warning_types.RemovedInPytest4Warning: Fixture "resp" called directly."""
    return client.get(reverse('core:profile'), secure=True)


@pytest.fixture
def user(django_user_model):
    usr = mommy.make(django_user_model)
    return usr


@pytest.fixture
def resp_with_user(user, client: Client):
    client.force_login(user)
    return _resp(client)


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


def test_edit_password_link(resp_with_user):
    dj_assert_contains(resp_with_user, reverse('core:profile_password'))


@pytest.fixture
def user_with_plain_password(django_user_model):
    plain_password = 'senha'
    u = mommy.make(django_user_model)
    u.set_password(plain_password)
    u.plain_password = plain_password
    u.save()
    return u


def test_email_normalization(user_with_plain_password, client, django_user_model):
    client.force_login(user_with_plain_password)
    email = 'ALUNO@PYTHON.PRO.BR'
    client.post(
        reverse('core:profile_email'),
        {'email': email, 'current_password': user_with_plain_password.plain_password},
        secure=True
    )
    saved_user = django_user_model.objects.first()
    assert saved_user.email == email.lower()
