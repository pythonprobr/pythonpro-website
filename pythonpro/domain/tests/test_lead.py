from unittest.mock import call

import pytest

from pythonpro.domain import user_facade


@pytest.fixture
def create_or_update_lead_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.create_or_update_lead.delay')


@pytest.fixture
def sync_user_delay(mocker):
    return mocker.patch('pythonpro.domain.user_facade.sync_user_on_discourse.delay')


def test_creation(db, django_user_model, create_or_update_lead_mock, sync_user_delay):
    user = user_facade.register_lead('Renzo Nuccitelli', 'renzo@python.pro.br', 'google_ads')
    calls = [call(user.first_name, user.email), call(user.first_name, user.email, id=user.id)]
    create_or_update_lead_mock.assert_has_calls(calls)
    sync_user_delay.assert_called_once_with(user.id)
    assert django_user_model.objects.all().get() == user


def test_should_create_lead_with_extra_tags(
    db, django_user_model, create_or_update_lead_mock, sync_user_delay
):
    user = user_facade.register_lead(
        'Renzo Nuccitelli', 'renzo@python.pro.br', 'google_ads', tags=['tag-1', 'tag-2']
    )
    calls = [
        call(user.first_name, user.email, 'tag-1', 'tag-2'),
        call(user.first_name, user.email, 'tag-1', 'tag-2', id=user.id)
    ]
    create_or_update_lead_mock.assert_has_calls(calls)
    sync_user_delay.assert_called_once_with(user.id)
    assert django_user_model.objects.all().get() == user
