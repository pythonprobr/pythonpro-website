import pytest

from pythonpro import facade


@pytest.fixture
def create_or_update_lead_mock(mocker):
    return mocker.patch('pythonpro.facade._mailchimp_facade.create_or_update_lead')


def test_creation(db, django_user_model, create_or_update_lead_mock):
    user = facade.register_lead('Renzo Nuccitelli', 'renzo@python.pro.br', 'google_ads')
    create_or_update_lead_mock.assert_called_once_with('Renzo Nuccitelli', 'renzo@python.pro.br')
    assert django_user_model.objects.all().get() == user
