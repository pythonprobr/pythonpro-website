import pytest
from django.test import Client
from django.urls import reverse
from faker import Faker
from model_mommy import mommy

from pythonpro.core.models import User
from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def resp(client: Client):
    return _resp(client)


def _resp(client: Client):
    """Plain function to avoid _pytest.warning_types.RemovedInPytest4Warning: Fixture "resp" called directly."""
    return client.get(reverse('core:profile_email'), secure=True)


@pytest.fixture
def user(django_user_model):
    usr = mommy.make(django_user_model)
    return usr


@pytest.fixture
def resp_with_user(user, client: Client):
    client.force_login(user)
    return _resp(client)


def test_not_logged_user(resp):
    assert 302 == resp.status_code


def test_logged_status_code(resp_with_user):
    assert 200 == resp_with_user.status_code


def test_profile_email(user, resp_with_user):
    dj_assert_contains(resp_with_user, user.email)


@pytest.mark.parametrize(
    'data',
    [
        '<form method="post"',
        '<input type="email" name="email',
        '<input type="password" name="current_password',
        'type="submit',
    ]
)
def test_form_data(data, resp_with_user):
    dj_assert_contains(resp_with_user, data)


def test_edit_email(django_user_model, fake: Faker, user: User, client: Client):
    password = 'password'
    user.set_password(password)
    user.save()
    client.force_login(user)
    email = fake.email()
    client.post(reverse('core:profile_email'), {'email': email, 'current_password': password}, secure=True)
    assert email == django_user_model.objects.filter(pk=user.pk).get().email


def test_not_edit_email_wrong_password(django_user_model, fake: Faker, user: User, client: Client):
    """Assert email can't be change using wrong password """
    user.set_password('password')
    user.save()
    client.force_login(user)
    old_email = user.email
    resp = client.post(reverse('core:profile_email'), {'email': fake.email(), 'current_password': 'wrong'}, secure=True)
    assert old_email == django_user_model.objects.filter(pk=user.pk).get().email
    assert 200 == resp.status_code


def test_email_error_msg(fake: Faker, user: User, client: Client):
    """Assert email can't be change using wrong password """
    user.set_password('password')
    user.save()
    client.force_login(user)
    resp = client.post(reverse('core:profile_email'), {'email': fake.email(), 'current_password': 'wrong'}, secure=True)
    dj_assert_contains(resp, 'Senha Inválida')
