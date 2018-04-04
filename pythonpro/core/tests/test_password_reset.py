import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def reset_password_resp(client):
    return client.get(reverse('password_reset'))


def test_email_form_status(reset_password_resp):
    reset_password_resp.status = 200


@pytest.mark.parametrize(
    'content',
    [
        '<input type="email"',
        'type="submit"',
    ]
)
def test_email_form_content(content, reset_password_resp):
    dj_assert_contains(reset_password_resp, content)


def test_reset_done(client):
    resp = client.get(reverse('password_reset_done'))
    assert resp.status_code == 200
