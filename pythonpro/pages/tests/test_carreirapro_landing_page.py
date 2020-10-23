import pytest

from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


def test_should_return_200_when_load_invite_page(client):
    resp = client.get(reverse('pages:ds_webinar_landing_page'))
    assert resp.status_code == 200


def test_should_return_200_when_load_thank_you_page(client):
    resp = client.get(reverse('pages:ds_webinar_thank_you_page'))
    assert resp.status_code == 200


@pytest.fixture
def subscribe_with_no_role(mocker):
    return mocker.patch('pythonpro.domain.subscription_domain.subscribe_with_no_role.delay')


def test_should_run_form_ok(subscribe_with_no_role, client):
    resp = client.post(
        reverse('pages:ds_webinar_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br'},
        secure=True
    )

    assert resp.status_code == 302


def test_should_inform_form_error(subscribe_with_no_role, client):
    resp = client.post(
        reverse('pages:ds_webinar_landing_page'),
        {'name': 'Moacir', 'email': 'moacirpython.pro.br'},
        secure=True
    )

    assert resp.status_code == 200
    dj_assert_contains(resp, 'is-invalid')
