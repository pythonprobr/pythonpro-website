import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def login_get_resp(client, db):
    return client.get(reverse('login'), secure=True)


def test_page_status(login_get_resp):
    login_get_resp.status = 200


@pytest.mark.parametrize(
    'content',
    [
        '<form',
        '<input type="email" name="username"',
        '<input type="password" name="password"',
        'type="submit"',
    ]
)
def test_page_content(content, login_get_resp):
    dj_assert_contains(login_get_resp, content)
