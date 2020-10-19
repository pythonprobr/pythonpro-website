from unittest import mock

import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def client(client, cohort):
    return client


def test_should_return_200_when_load_invite_page(client):
    resp = client.get(reverse('pages:bootcamp_vip_landing_page'))
    assert resp.status_code == 200


def test_should_return_200_when_load_thank_you_page(client):
    resp = client.get(reverse('pages:bootcamp_vip_thank_you_page'))
    assert resp.status_code == 200


def test_should_load_name_and_email_when_it_comes_by_GET(client):
    resp = client.get(reverse('pages:bootcamp_vip_landing_page'), data={
        'name': 'Moacir', 'email': 'moacir@python.pro.br', 'phone': '(11) 99999-9999'
    })
    dj_assert_contains(resp, 'Moacir')
    dj_assert_contains(resp, 'moacir@python.pro.br')
    dj_assert_contains(resp, '(11) 99999-9999')


def test_should_load_name_and_email_when_user_is_logged(client_with_user, logged_user):
    resp = client_with_user.get(reverse('pages:bootcamp_vip_landing_page'))
    dj_assert_contains(resp, logged_user.first_name)
    dj_assert_contains(resp, logged_user.email)


def test_should_load_name_and_email_from_GET_when_user_is_logged(client_with_user, logged_user):
    resp = client_with_user.get(reverse('pages:bootcamp_vip_landing_page'), data={
        'name': 'Moacir', 'email': 'moacir@python.pro.br', 'phone': '(11) 99999-9999'
    })
    dj_assert_contains(resp, 'Moacir')
    dj_assert_contains(resp, 'moacir@python.pro.br')
    dj_assert_contains(resp, '(11) 99999-9999')


@pytest.fixture
def subscribe_with_no_role(mocker):
    return mocker.patch('pythonpro.domain.subscription_domain.subscribe_with_no_role.delay')


# TODO: move this phone tests do generic context
def test_should_call_update_when_with_correct_parameters(subscribe_with_no_role, client):
    client.post(
        reverse('pages:bootcamp_vip_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br', 'phone': '(11) 99999-9999'},
        secure=True
    )

    subscribe_with_no_role.assert_called_with(
        None, 'Moacir', 'moacir@python.pro.br', mock.ANY, phone='+5511999999999'
    )


# TODO: move this phone tests do generic context
def test_should_call_update_when_logged_with_correct_parameters(subscribe_with_no_role, client_with_user):
    resp_with_user = client_with_user.post(
        reverse('pages:bootcamp_vip_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br', 'phone': '(11) 99999-9999'},
        secure=True
    )

    subscribe_with_no_role.assert_called_with(
        resp_with_user.cookies['sessionid'].value,
        'Moacir',
        'moacir@python.pro.br',
        mock.ANY,
        id=mock.ANY,
        phone='+5511999999999'
    )


def test_should_run_form_ok(subscribe_with_no_role, client, cohort):
    resp = client.post(
        reverse('pages:bootcamp_vip_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br', 'phone': '(11) 99999-9999'},
        secure=True
    )

    assert resp.status_code == 302


def test_should_inform_form_error(subscribe_with_no_role, client, cohort):
    resp = client.post(
        reverse('pages:bootcamp_vip_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br'},
        secure=True
    )

    assert resp.status_code == 200
    dj_assert_contains(resp, 'is-invalid')
