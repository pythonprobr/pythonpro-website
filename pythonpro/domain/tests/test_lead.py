from unittest.mock import call

import pytest

from pythonpro.domain import user_facade


@pytest.fixture
def create_or_update_lead_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.create_or_update_lead')


@pytest.fixture
def sync_user(mocker):
    return mocker.patch('pythonpro.domain.user_facade._discourse_facade.sync_user')


def test_creation(db, django_user_model, create_or_update_lead_mock, sync_user):
    user = user_facade.register_lead('Renzo Nuccitelli', 'renzo@python.pro.br', 'google_ads')
    calls = [call(user.first_name, user.email), call(user.first_name, user.email, id=user.id)]
    create_or_update_lead_mock.assert_has_calls(calls)
    sync_user.assert_called_once_with(user)
    assert django_user_model.objects.all().get() == user
