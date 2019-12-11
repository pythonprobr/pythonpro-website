from unittest.mock import call

import pytest

from pythonpro.domain import user_facade


@pytest.fixture
def create_or_update_lead_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.create_or_update_lead')


def test_creation(db, django_user_model, create_or_update_lead_mock):
    user = user_facade.register_lead('Renzo Nuccitelli', 'renzo@python.pro.br', 'google_ads')
    calls = [call(user.first_name, user.email), call(user.first_name, user.email, id=user.id)]
    create_or_update_lead_mock.assert_has_calls(calls)
    assert django_user_model.objects.all().get() == user
