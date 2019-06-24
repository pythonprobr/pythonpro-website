from unittest.mock import Mock

import pytest
from django.urls import reverse
from faker import Faker
from rolepermissions.checkers import has_role


@pytest.fixture
def resp(client):
    return client.get(reverse('core:lead_landing'), secure=True)


def test_status_code(resp):
    assert 200 == resp.status_code


@pytest.fixture
def create_lead_mock(mocker):
    return mocker.patch('pythonpro.core.views.facade.create_or_update_lead')


@pytest.fixture
def resp_lead_creation(client, db, fake: Faker, create_lead_mock):
    client.post(
        reverse('core:lead_form') + '?utm_source=facebook',
        data={
            'first_name': fake.name(),
            'email': fake.email(),
        },
        secure=True
    )


def test_lead_creation(resp_lead_creation, django_user_model):
    assert django_user_model.objects.exists()


def test_user_has_role(resp_lead_creation, django_user_model):
    user = django_user_model.objects.first()
    assert has_role(user, 'lead')


def test_user_created_as_lead_on_mailchimp(resp_lead_creation, django_user_model, create_lead_mock: Mock):
    user = django_user_model.objects.first()
    create_lead_mock.assert_called_once_with(user.first_name, user.email)


def test_user_source_was_saved_from_url(resp_lead_creation, django_user_model, create_lead_mock: Mock):
    user = django_user_model.objects.first()
    assert user.source == 'facebook'
