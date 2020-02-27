from unittest.mock import Mock, call

import pytest
from django.urls import reverse
from faker import Faker
from rolepermissions.checkers import has_role
from rolepermissions.roles import assign_role, remove_role

from pythonpro.absolute_uri import build_absolute_uri
from pythonpro.core.models import UserInteraction
from pythonpro.django_assertions import dj_assert_not_contains


@pytest.fixture
def resp(client):
    return client.get(reverse('core:lead_landing'), secure=True)


def test_status_code(resp):
    assert 200 == resp.status_code


def test_there_is_no_none_on_landing_page(resp):
    """
    Assert there is no None field on home form
    """
    dj_assert_not_contains(resp, 'value="None"')


@pytest.fixture
def create_lead_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.create_or_update_lead')


@pytest.fixture()
def email(fake):
    return fake.email()


@pytest.fixture
def resp_lead_creation(client, db, fake: Faker, create_lead_mock, email):
    return client.post(
        reverse('core:lead_form') + '?utm_source=facebook',
        data={
            'first_name': fake.name(),
            'email': email,
        },
        secure=True
    )


def test_email_error_subscribing_with_email_variation(resp_lead_creation, email: str, fake, client):
    email_upercase = email.upper()
    resp = client.post(
        reverse('core:lead_form') + '?utm_source=facebook',
        data={
            'first_name': fake.name(),
            'email': email_upercase,
        },
        secure=True
    )

    assert resp.status_code == 400


@pytest.fixture
def resp_email_upper_case(client, db, fake: Faker, create_lead_mock, email):
    email = email.upper()
    return client.post(
        reverse('core:lead_form') + '?utm_source=facebook',
        data={
            'first_name': fake.name(),
            'email': email,
        },
        secure=True
    )


def test_email_normalization(resp_email_upper_case, email, django_user_model):
    email_lower = email.lower()
    user = django_user_model.objects.first()
    assert user.email == email_lower


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


@pytest.fixture(autouse=True)
def sync_user(mocker):
    return mocker.patch('pythonpro.domain.user_facade._discourse_facade.sync_user')


def test_user_discourse_sync(resp_lead_creation, django_user_model, sync_user):
    user = django_user_model.objects.first()
    sync_user.assert_called_once_with(user)


def test_lead_creation(resp_lead_creation, django_user_model):
    assert django_user_model.objects.exists()


def test_lead_created_interaction(resp_lead_creation, django_user_model):
    user = django_user_model.objects.get()
    interaction = UserInteraction.objects.filter(category=UserInteraction.BECOME_LEAD, user=user).get()
    assert interaction.source == 'facebook'


@pytest.fixture
def resp_lead_creation_without_source(client, db, fake: Faker, create_lead_mock):
    return client.post(
        reverse('core:lead_form'),
        data={
            'first_name': fake.name(),
            'email': fake.email(),
        },
        secure=True
    )


def test_lead_from_unknow_source(resp_lead_creation_without_source, django_user_model):
    user = django_user_model.objects.get()
    assert user.source == 'unknown'


def test_password_email_sent(resp_lead_creation_without_source, django_user_model, mailoutbox):
    assert len(mailoutbox) == 1
    body = mailoutbox[0].body
    assert build_absolute_uri(reverse('core:profile_password')) in body


def test_user_has_role(resp_lead_creation, django_user_model):
    user = django_user_model.objects.first()
    assert has_role(user, 'lead')


def test_user_created_as_lead_on_email_marketing(resp_lead_creation, django_user_model, create_lead_mock: Mock):
    user = django_user_model.objects.first()
    calls = [call(user.first_name, user.email), call(user.first_name, user.email, id=user.id)]
    create_lead_mock.assert_has_calls(calls)


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


def test_should_redirect_to_OTO_page(resp_lead_creation):
    assert resp_lead_creation['Location'] == reverse('payments:client_landing_page_oto')


def test_should_has_a_lite_version(client):
    assert client.get(reverse('core:lead_landing_lite'), secure=True)


@pytest.fixture
def resp_lead_creation_without_OTO(client, db, fake: Faker, create_lead_mock, email):
    return client.post(
        reverse('core:lead_landing_without_OTO'),
        data={
            'first_name': fake.name(),
            'email': email,
        },
        secure=True
    )


def test_should_has_a_version_that_not_redirect_to_OTO_page(resp_lead_creation_without_OTO):
    assert resp_lead_creation_without_OTO['Location'] == reverse('core:thanks')
