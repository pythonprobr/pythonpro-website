from unittest import mock

import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def client(client, cohort):
    return client


def test_should_return_200_when_load_invite_page(client):
    resp = client.get(reverse('pages:tpp_masterclass_landing_page'))
    assert resp.status_code == 200


@pytest.fixture
def subscribe_with_no_role(mocker):
    return mocker.patch('pythonpro.domain.subscription_domain.subscribe_with_no_role.delay')


# TODO: move this phone tests do generic context
def test_should_call_update_when_with_correct_parameters(subscribe_with_no_role, client):
    client.post(
        reverse('pages:tpp_masterclass_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br'},
        secure=True
    )

    subscribe_with_no_role.assert_called_with(None, 'Moacir', 'moacir@python.pro.br', mock.ANY)


# TODO: move this phone tests do generic context
def test_should_call_update_when_logged_with_correct_parameters(subscribe_with_no_role,
                                                                client_with_user):
    resp_with_user = client_with_user.post(
        reverse('pages:tpp_masterclass_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br'},
        secure=True
    )

    subscribe_with_no_role.assert_called_with(
        resp_with_user.cookies['sessionid'].value,
        'Moacir',
        'moacir@python.pro.br',
        mock.ANY
    )


def test_should_run_form_ok(subscribe_with_no_role, client, cohort):
    resp = client.post(
        reverse('pages:tpp_masterclass_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br'},
        secure=True
    )

    assert resp.status_code == 302


def test_should_inform_form_error(subscribe_with_no_role, client, cohort):
    resp = client.post(
        reverse('pages:tpp_masterclass_landing_page'),
        {'name': 'Moacir', 'email': 'moacirpython.pro.br'},
        secure=True
    )

    assert resp.status_code == 200
    dj_assert_contains(resp, 'is-invalid')


def test_should_return_200_when_load_thank_you_page(client):
    resp = client.get(reverse('pages:tpp_masterclass_thank_you_page'))
    assert resp.status_code == 200
