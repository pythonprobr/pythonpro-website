import pytest
from django.urls import reverse


@pytest.fixture
def login_get_resp(client, db):
    return client.get(reverse('two_factor:login'), secure=True)


def test_page_status(login_get_resp):
    login_get_resp.status = 200
