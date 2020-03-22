import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.domain.user_facade import find_user_interactions


@pytest.fixture
def resp(client):
    return client.get(reverse('launch:landing_page'), secure=True)


def test_status_code(resp):
    assert 200 == resp.status_code


def test_email_field_is_present(resp):
    dj_assert_contains(resp, 'type="email" name="email"')


def test_submmit_button_is_present(resp):
    dj_assert_contains(resp, 'type="submit"')


def test_form_action_is_present(resp):
    dj_assert_contains(resp, f'action="{reverse("launch:lead_form")}" method="POST"')


@pytest.fixture
def resp_with_user(client_with_user):
    return client_with_user.get(reverse('launch:landing_page'), secure=True)


def test_user_interaction(resp_with_user, logged_user):
    assert 'LAUNCH_LP' in [i.category for i in find_user_interactions(logged_user)]
