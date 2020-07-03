import pytest
from django.test import Client
from django.urls import reverse
from model_mommy import mommy

from pythonpro.core.models import User
from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def resp(client: Client):
    return _resp(client)


def _resp(client):
    """Plain function to avoid _pytest.warning_types.RemovedInPytest4Warning: Fixture "resp" called directly."""
    return client.get(reverse('core:profile_password'))


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


@pytest.mark.parametrize(
    'data',
    [
        '<form method="post"',
        '<input type="password" name="old_password',
        '<input type="password" name="new_password1',
        '<input type="password" name="new_password2',
        'type="submit',
    ]
)
def test_form_data(data, resp_with_user):
    dj_assert_contains(resp_with_user, data)


def test_edit_password(django_user_model, user: User, client: Client):
    old_password = 'old password'
    user.set_password(old_password)
    user.save()
    client.force_login(user)
    new_password = 'Q!W@E#R$T%'
    client.post(
        reverse('core:profile_password'),
        {
            'old_password': old_password,
            'new_password1': new_password,
            'new_password2': new_password,
        },
        secure=True)
    user = django_user_model.objects.filter(pk=user.pk).get()
    assert user.check_password(new_password)
