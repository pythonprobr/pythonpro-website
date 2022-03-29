from unittest.mock import Mock, call, ANY

import pytest
from django.urls import reverse
from faker import Faker
from model_bakery import baker
from pytest_django.asserts import assertRedirects
from rolepermissions.checkers import has_role
from rolepermissions.roles import assign_role, remove_role

from pythonpro.absolute_uri import build_absolute_uri
from pythonpro.core.models import UserInteraction
from pythonpro.django_assertions import (dj_assert_contains, dj_assert_not_contains, dj_assert_template_used)


@pytest.fixture
def resp(client):
    return client.get(reverse('core:lead_landing'))


def test_status_code(resp):
    assert 200 == resp.status_code


def test_there_is_no_none_on_landing_page(resp):
    """
    Assert there is no None field on home form
    """
    dj_assert_not_contains(resp, 'value="None"')


@pytest.fixture(params='superadmin data_scientist'.split())
@pytest.mark.django_db
def superuser(django_user_model, request):
    role = request.param
    if role == 'superadmin':
        return baker.make(django_user_model, is_superuser=True)
    data_scientist = baker.make(django_user_model, is_superuser=False)
    assign_role(data_scientist, role)
    return data_scientist


@pytest.fixture
def resp_with_superuser(client, superuser):
    client.force_login(superuser)
    return client.get(reverse('core:lead_landing'))


def test_superuser_can_access_landing_page(resp_with_superuser):
    assert resp_with_superuser.status_code == 200


@pytest.fixture(params='lead client webdev member'.split())
@pytest.mark.django_db
def user_with_webdev_roles(django_user_model, request):
    role = request.param
    user = baker.make(django_user_model, is_superuser=False)
    assign_role(user, role)
    return user


@pytest.fixture
def resp_with_user_with_webdev_roles(client, user_with_webdev_roles):
    client.force_login(user_with_webdev_roles)
    return client.get(reverse('core:lead_landing'))


def test_user_with_webdev_roles_can_access_landing_page(resp_with_user_with_webdev_roles):
    assertRedirects(resp_with_user_with_webdev_roles, reverse('dashboard:home'), status_code=301,
                    target_status_code=200)
    # assert resp_with_user_with_webdev_roles.status_code == 301
    # assert resp_with_user_with_webdev_roles.url == reverse('dashboard:home')


@pytest.fixture
def create_lead_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.create_or_update_lead.delay')


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
            'phone': '(11)966922655',
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
            'phone': '(11)966922655',
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
            'phone': '(11)966922655',
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
def sync_user_delay(mocker):
    return mocker.patch('pythonpro.domain.user_domain.sync_user_on_discourse.delay')


def test_user_discourse_sync(resp_lead_creation, sync_user_delay):
    assert not sync_user_delay.called


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
            'phone': '(11)966922655',
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
    create_lead_mock.assert_called_once_with(user.first_name, user.email, 'offer-funnel-0', 'utm_source=facebook',
                                             phone="11966922655", id=user.id, utm_source='facebook')


def test_user_source_was_saved_from_url(resp_lead_creation, django_user_model, create_lead_mock: Mock):
    user = django_user_model.objects.first()
    assert user.source == 'facebook'


def test_user_was_logged_in(resp_lead_creation, django_user_model, client):
    response = client.get(reverse('core:lead_change_password'))
    assert response.status_code == 200


def test_user_change_password_should_run_ok(resp_lead_change_pasword, django_user_model):
    user = django_user_model.objects.first()
    assert user.check_password('senha-muito-d1f1c1l')


def test_only_role_lead_can_change_password(resp_lead_change_pasword, django_user_model, client):
    user = django_user_model.objects.first()
    assign_role(user, 'member')
    remove_role(user, 'lead')

    response = client.get(reverse('core:lead_change_password'))
    assert response.status_code == 302


def test_should_has_a_normal_version(resp):
    dj_assert_template_used(resp, 'core/lead_landing_page.html')


def test_should_has_a_lite_version(client):
    resp = client.get(reverse('core:lead_landing_lite'))
    dj_assert_template_used(resp, 'core/lead_landing_lite_page.html')


def test_should_use_lead_form_with_no_offer(client):
    resp = client.get(reverse('core:lead_landing_with_no_offer'))
    dj_assert_not_contains(resp, reverse('core:lead_form') + '"')
    dj_assert_contains(resp, reverse('core:lead_form_with_no_offer'))


def test_should_use_lead_form_with_OTO(resp):
    dj_assert_contains(resp, reverse('core:lead_form'))
    dj_assert_not_contains(resp, reverse('core:lead_form_with_no_offer'))


@pytest.fixture
def resp_lead_creation_with_no_offer(client, db, fake: Faker, create_lead_mock, email):
    return client.post(
        reverse('core:lead_form_with_no_offer'),
        data={
            'first_name': fake.name(),
            'email': email,
            'phone': "(11)966922655",
        },
        secure=True
    )


def test_should_redirect_to_thanks_page_direclty(resp_lead_creation_with_no_offer):
    assert resp_lead_creation_with_no_offer['Location'] == reverse('core:thanks')


@pytest.fixture
def qs_with_utms():
    return (
        "?utm_source=facebook-ads"
        "&utm_medium=trafego-pago"
        "&utm_campaign=a00f00"
        "&utm_content=content"
        "&utm_term=term"
        "&fbclid=584954"
    )


@pytest.fixture
def url_with_utms(qs_with_utms):
    return reverse('core:lead_form_with_no_offer') + qs_with_utms


@pytest.fixture
def resp_lead_creation_with_utms(client, db, fake: Faker, create_lead_mock, email, url_with_utms):
    return client.post(
        url_with_utms,
        data={
            'first_name': fake.name(),
            'email': email,
            'phone': "(11)966922655",
        },
        secure=True
    )


def test_should_send_utms_to_email_marketing_as_tags(create_lead_mock, resp_lead_creation_with_utms):
    calls = [
        call(
            ANY,
            ANY,
            'offer-funnel-1',
            "utm_source=facebook-ads",
            "utm_medium=trafego-pago",
            "utm_campaign=a00f00",
            "utm_content=content",
            "utm_term=term",
            phone='11966922655',
            id=ANY,
            utm_source='facebook-ads'
        )
    ]
    create_lead_mock.assert_has_calls(calls)


def test_should_not_send_other_params_than_utms_to_email_marketing_as_tags(
        create_lead_mock, resp_lead_creation_with_utms
):
    for current_call in create_lead_mock.call_args_list:
        assert 'fbclid=584954' not in current_call


@pytest.fixture
def resp_with_utm(client, qs_with_utms):
    return client.get(reverse('core:lead_landing') + qs_with_utms)


def test_should_send_utms_to_form_action(qs_with_utms, resp_with_utm):
    dj_assert_contains(resp_with_utm, qs_with_utms)
