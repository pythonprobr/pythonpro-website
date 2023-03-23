from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from pythonpro.memberkit import facade, api
from pythonpro.memberkit.models import SubscriptionType, Subscription


@pytest.fixture
def api_key():
    key = 'some_key'
    api.set_default_api_key(key)
    return key


@pytest.fixture(autouse=True)
def enable_memberkit(settings):
    settings.MEMBERKIT_ON = True


@pytest.mark.freeze_time('2021-06-09')
def test_activate_on_membership(django_user_model, logged_user, responses, api_key):
    memberkit_user_id = 5047080
    user_response = {
        'bio': None,
        'blocked': False,
        'email': 'renzo@python.pro.br',
        'enrollments': [],
        'full_name': 'ktGsanrofXZhsxXakxkNtHTNiDRdQU',
        'id': memberkit_user_id,
        'memberships': [
            {
                'expire_date': '2200-01-01',
                'membership_level_id': 4424,
                'status': 'active'
            }
        ],
        'profile_image_url': None,
        'unlimited': True
    }
    user = baker.make(django_user_model, email='renzo@python.pro.br')
    responses.add(
        responses.POST,
        f'https://memberkit.com.br/api/v1/users?api_key={api_key}',
    )
    responses.add(
        responses.GET,
        f'https://memberkit.com.br/api/v1/users/{user.email}?api_key={api_key}',
        json=user_response
    )
    subscription_type = SubscriptionType.objects.create(id=4424, name='Membros')
    subscription = baker.make(
        Subscription,
        subscriber=user,
        status=Subscription.Status.INACTIVE,
        activated_at=None,
        memberkit_user_id=None
    )
    subscription.subscription_types.add(subscription_type)
    msg = 'Ativado via admin'
    facade.activate(subscription, logged_user, msg)
    subscription.refresh_from_db()
    assert subscription.status == Subscription.Status.ACTIVE
    assert subscription.activated_at == timezone.now()
    assert subscription.memberkit_user_id == memberkit_user_id
    assert subscription.observation == msg
    assert subscription.responsible == logged_user


# Esses ids de comunidade são os verdadeiros de produção, que foram extraidos do memberkit
@pytest.mark.parametrize('comunidade_id', [11610, 12180])
@pytest.mark.freeze_time('2023-03-22')
def test_comunidade_devpro_date_extension(django_user_model, comunidade_id, mocker):
    memberkit_user_id_response = {'id': 56}
    mocker.patch('pythonpro.memberkit.facade.api.activate_user', return_value=memberkit_user_id_response)
    user = baker.make(django_user_model, email='renzo@python.pro.br')
    renovation_days_of_access = 365

    subscription_type_comunidade = SubscriptionType.objects.create(
        id=comunidade_id,
        name='Comunidade Devpro',
        days_of_access=renovation_days_of_access
    )

    subscription_to_be_activated = baker.make(
        Subscription,
        subscriber=user,
        status=Subscription.Status.INACTIVE,
        activated_at=None,
        memberkit_user_id=None
    )
    subscription_to_be_activated.subscription_types.add(subscription_type_comunidade)

    comunidade_days_of_access = 90
    comunidade_days_consumed = 87
    comunidade_activation_date = timezone.now() - timedelta(comunidade_days_consumed)
    subscription_comunidade = baker.make(
        Subscription,
        subscriber=user,
        status=Subscription.Status.ACTIVE,
        activated_at=comunidade_activation_date,
        days_of_access=comunidade_days_of_access,
        memberkit_user_id=None
    )

    subscription_comunidade.subscription_types.add(subscription_type_comunidade)

    facade.activate(subscription_to_be_activated)
    subscription_to_be_activated.refresh_from_db()
    remaining_comunidade_days = comunidade_days_of_access - comunidade_days_consumed
    assert (subscription_to_be_activated.expires_at ==
            timezone.now() +
            timedelta(renovation_days_of_access + remaining_comunidade_days)
            )


def test_deactivate_on_membership(django_user_model, logged_user, api_key, responses):
    memberkit_user_id = 5047080
    user_response = {
        'bio': None,
        'blocked': False,
        'email': 'renzo@python.pro.br',
        'enrollments': [],
        'full_name': 'ktGsanrofXZhsxXakxkNtHTNiDRdQU',
        'id': memberkit_user_id,
        'memberships': [
            {
                'expire_date': '2200-01-01',
                'membership_level_id': 4424,
                'status': 'active'
            }
        ],
        'profile_image_url': None,
        'unlimited': True
    }
    user = baker.make(django_user_model, email='renzo@python.pro.br')
    responses.add(
        responses.GET,
        f'https://memberkit.com.br/api/v1/users/{memberkit_user_id}?api_key={api_key}',
        json=user_response
    )

    inactive_user_response = {
        'bio': None,
        'blocked': False,
        'email': 'renzo@python.pro.br',
        'enrollments': [],
        'full_name': 'ktGsanrofXZhsxXakxkNtHTNiDRdQU',
        'id': memberkit_user_id,
        'memberships': [
            {
                'expire_date': '2200-01-01',
                'membership_level_id': 4424,
                'status': 'expired'
            }
        ],
        'profile_image_url': None,
        'unlimited': True
    }
    responses.add(
        responses.POST,
        f'https://memberkit.com.br/api/v1/users?api_key={api_key}',
        json=inactive_user_response
    )

    subscription_type = SubscriptionType.objects.create(id=4424, name='Membros')
    subscription = baker.make(
        Subscription,
        subscriber=user,
        status=Subscription.Status.ACTIVE,
        activated_at=timezone.now(),
        memberkit_user_id=memberkit_user_id
    )
    subscription.subscription_types.add(subscription_type)
    msg = 'Desativado por razão x'
    facade.inactivate(subscription, logged_user, msg)
    subscription.refresh_from_db()
    assert subscription.status == Subscription.Status.INACTIVE
    assert subscription.activated_at is None
    assert subscription.memberkit_user_id == memberkit_user_id
    assert subscription.observation == msg
    assert subscription.responsible == logged_user
