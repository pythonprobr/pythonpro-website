import pytest
from django.shortcuts import resolve_url


@pytest.fixture()
def home_resp(client):
    return client.get(resolve_url('/'))


def test_home_status_code(home_resp):
    assert 200 == home_resp.status_code


def test_home_template(home_resp):
    assert 'core/index.html' == home_resp.templates[0].name
