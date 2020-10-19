import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def email(fake):
    return fake.email().lower()


@pytest.fixture
def email_upper(email):
    return email.upper()


@pytest.fixture
def subscribe_with_no_role(mocker):
    return mocker.patch('pythonpro.launch.views.subscription_domain.subscribe_with_no_role.delay')


@pytest.fixture
def resp(client, email, subscribe_with_no_role, cohort):
    return client.post(reverse('launch:lead_form'), {'email': email, 'name': 'Moacir'})


@pytest.fixture
def resp_email_upper(client, email_upper, subscribe_with_no_role, cohort):
    return client.post(reverse('launch:lead_form'), {'email': email_upper, 'name': 'Moacir'})


@pytest.fixture
def invalid_email(email):
    return f'@{email}'


def test_status_code(resp):
    assert 302 == resp.status_code


def test_email_marketing_sucess_integration(resp, email, subscribe_with_no_role, cohort):
    subscribe_with_no_role.assert_called_once_with(None, 'Moacir', email,
                                                   f'turma-{cohort.slug}-semana-do-programador')


def test_email_normalization(resp_email_upper, email, subscribe_with_no_role, cohort):
    subscribe_with_no_role.assert_called_once_with(None, 'Moacir', email,
                                                   f'turma-{cohort.slug}-semana-do-programador')


@pytest.fixture
def resp_with_error(client, invalid_email, subscribe_with_no_role):
    return client.post(reverse('launch:lead_form'), {'email': invalid_email, 'name': 'Moacir'})


def test_email_marketing_not_executed_on_error(resp_with_error, subscribe_with_no_role):
    assert subscribe_with_no_role.call_count == 0


def test_status_code_error(resp_with_error):
    assert 400 == resp_with_error.status_code


def test_email_field_is_present(resp_with_error):
    dj_assert_contains(resp_with_error, 'type="email" name="email"', status_code=400)


def test_submmit_button_is_present(resp_with_error):
    dj_assert_contains(resp_with_error, 'type="submit"', status_code=400)


def test_form_action_is_present(resp_with_error):
    dj_assert_contains(resp_with_error, f'action="{reverse("launch:lead_form")}" method="POST"', status_code=400)


@pytest.fixture
def resp_with_user(client_with_user, logged_user, cohort, subscribe_with_no_role):
    return client_with_user.post(
        reverse('launch:lead_form'), {'email': logged_user.email, 'name': 'Moacir'})


def test_user_first_name(resp_with_user, logged_user, subscribe_with_no_role, cohort):
    subscribe_with_no_role.assert_called_once_with(
        resp_with_user.cookies['sessionid'].value,
        'Moacir',
        logged_user.email,
        f'turma-{cohort.slug}-semana-do-programador',
        id=logged_user.id
    )
