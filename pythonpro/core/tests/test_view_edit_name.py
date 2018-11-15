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
    return client.get(reverse('core:profile_name'), secure=True)


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


def test_profile_first_name(user, resp_with_user):
    dj_assert_contains(resp_with_user, user.first_name)


@pytest.mark.parametrize(
    'data',
    [
        '<form method="post"',
        '<input type="text" name="first_name',
        'type="submit',
    ]
)
def test_form_data(data, resp_with_user):
    dj_assert_contains(resp_with_user, data)


def test_edit_name(django_user_model, fake, user, client: Client):
    client.force_login(user)
    name = fake.name()
    client.post(reverse('core:profile_name'), {'first_name': name}, secure=True)
    assert name == django_user_model.objects.filter(pk=user.pk).get().first_name
