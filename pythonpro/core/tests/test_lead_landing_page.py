from unittest.mock import Mock

import pytest
from django.urls import reverse
from faker import Faker
from rolepermissions.checkers import has_role
from rolepermissions.roles import assign_role, remove_role


@pytest.fixture
def resp(client):
    return client.get(reverse('core:lead_landing'), secure=True)


def test_status_code(resp):
    assert 200 == resp.status_code


@pytest.fixture
def create_lead_mock(mocker):
    return mocker.patch('pythonpro.core.views.mailchimp_facade.create_or_update_lead')


@pytest.fixture
def resp_lead_creation(client, db, fake: Faker, create_lead_mock):
    return client.post(
        reverse('core:lead_form') + '?utm_source=facebook',
        data={
            'first_name': fake.name(),
            'email': fake.email(),
        },
        secure=True
    )


@pytest.fixture
def resp_lead_change_pasword(resp_lead_creation, client):
    client.post(
        reverse('core:lead_change_password'),
        data={
            'new_password1': 'senha-muito-d1f1c1l',
            'new_password2': 'senha-muito-d1f1c1l',
        },
        secure=True
    )


def test_lead_creation(resp_lead_creation, django_user_model):
    assert django_user_model.objects.exists()


def test_lead_from_unknow_source(resp_lead_creation, django_user_model, client, fake):
    email = fake.email()
    client.post(
        reverse('core:lead_form'),
        data={
            'first_name': fake.name(),
            'email': email,
        },
        secure=True
    )
    user = django_user_model.objects.filter(email=email).get()
    assert user.source == 'unknown'


def test_user_has_role(resp_lead_creation, django_user_model):
    user = django_user_model.objects.first()
    assert has_role(user, 'lead')


def test_user_created_as_lead_on_mailchimp(resp_lead_creation, django_user_model, create_lead_mock: Mock):
    user = django_user_model.objects.first()
    create_lead_mock.assert_called_once_with(user.first_name, user.email)


def test_user_source_was_saved_from_url(resp_lead_creation, django_user_model, create_lead_mock: Mock):
    user = django_user_model.objects.first()
    assert user.source == 'facebook'


def test_user_was_logged_in(resp_lead_creation, django_user_model, client):
    response = client.get(reverse('core:lead_change_password'), secure=True)
    assert response.status_code == 200


def test_user_change_password_should_run_ok(resp_lead_change_pasword, django_user_model):
    user = django_user_model.objects.first()
    assert user.check_password('senha-muito-d1f1c1l')


def test_only_role_lead_can_change_password(resp_lead_change_pasword, django_user_model, client):
    user = django_user_model.objects.first()
    assign_role(user, 'member')
    remove_role(user, 'lead')

    response = client.get(reverse('core:lead_change_password'), secure=True)
    assert response.status_code == 302
