import pytest
from django.urls import reverse


@pytest.fixture
def login_get_resp(client):
    return client.get(reverse('users:login'))


def test_page_status(login_get_resp):
    login_get_resp.status = 200
