import pytest

from pythonpro.domain import user_domain


@pytest.fixture
def create_or_update_lead_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.create_or_update_lead.delay')


@pytest.fixture
def sync_user_delay(mocker):
    return mocker.patch('pythonpro.domain.user_domain.sync_user_on_discourse.delay')


def test_creation(db, django_user_model, create_or_update_lead_mock, sync_user_delay):
    user = user_domain.register_lead('Renzo Nuccitelli', 'renzo@python.pro.br', 'google_ads', phone='11966922655')
    create_or_update_lead_mock.assert_called_once_with(
        user.first_name, user.email, id=user.id, phone='11966922655', utm_source='google_ads')
    assert not sync_user_delay.called
    assert django_user_model.objects.all().get() == user


def test_should_create_lead_with_extra_tags(
        db, django_user_model, create_or_update_lead_mock, sync_user_delay):
    user = user_domain.register_lead(
        'Renzo Nuccitelli', 'renzo@python.pro.br', 'google_ads', phone='11966922655', tags=['tag-1', 'tag-2']
    )
    create_or_update_lead_mock.assert_called_once_with(
        user.first_name, user.email, 'tag-1', 'tag-2', phone='11966922655', id=user.id, utm_source='google_ads'
    )
    assert not sync_user_delay.called
    assert django_user_model.objects.all().get() == user
