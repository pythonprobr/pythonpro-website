import pytest
from django.urls import reverse

from pythonpro.domain import user_domain


@pytest.fixture
def subscription_closed(settings):
    settings.SUBSCRIPTIONS_OPEN = False


@pytest.fixture
def subscribe_with_no_role_mock(mocker):
    subscribe_with_no_role = mocker.patch(
        'pythonpro.domain.user_domain.subscribe_with_no_role.delay'
    )
    return subscribe_with_no_role


@pytest.fixture
def resp(subscription_closed, client_with_lead, logged_user, subscribe_with_no_role_mock):
    logged_user.phone = '+5512997411854'  # only setting dynamic attribute for assertion purpose on tests
    data = {
        'email': logged_user.email,
        'first_name': logged_user.first_name,
        'phone': logged_user.phone
    }
    yield client_with_lead.post(reverse('checkout:bootcamp_lp'), data)


def test_logged_user_updated(resp, logged_user, subscribe_with_no_role_mock):
    subscribe_with_no_role_mock.assert_called_once_with(
        resp.cookies['sessionid'].value,
        logged_user.first_name,
        logged_user.email,
        'lista-de-espera',
        id=logged_user.id,
        phone=logged_user.phone
    )


def test_status_code(resp):
    assert resp.status_code == 302
    assert resp.url == reverse('checkout:waiting_list_ty')


def test_user_interacton(resp, logged_user):
    assert 'WAITING_LIST' == user_domain.find_user_interactions(logged_user)[0].category


@pytest.fixture
def resp_anonymous_user_existing_email(subscription_closed, client, logged_user, subscribe_with_no_role_mock):
    logged_user.phone = '+5512997411854'  # only setting dynamic attribute for assertion purpose on tests
    data = {
        'email': logged_user.email,
        'first_name': logged_user.first_name,
        'phone': logged_user.phone
    }
    yield client.post(reverse('checkout:bootcamp_lp'), data)


def test_anonymous_user_existing_email_updated(resp_anonymous_user_existing_email, logged_user,
                                               subscribe_with_no_role_mock):
    subscribe_with_no_role_mock.assert_called_once_with(
        None, logged_user.first_name, logged_user.email, 'lista-de-espera', id=logged_user.id, phone=logged_user.phone
    )


@pytest.fixture
def anonymous_form_data():
    return {
        'email': 'renzo@python.pro.br',
        'first_name': 'Renzo',
        'phone': '+5512997411854'
    }


@pytest.fixture
def resp_anonymous_user_missing_email(subscription_closed, client, subscribe_with_no_role_mock,
                                      anonymous_form_data, db):
    yield client.post(reverse('checkout:bootcamp_lp'), anonymous_form_data)


def test_anonymous_user_missing_email_updated(resp_anonymous_user_missing_email, anonymous_form_data,
                                              subscribe_with_no_role_mock):
    subscribe_with_no_role_mock.assert_called_once_with(
        None,
        anonymous_form_data['first_name'],
        anonymous_form_data['email'],
        'lista-de-espera',
        phone=anonymous_form_data['phone']
    )
