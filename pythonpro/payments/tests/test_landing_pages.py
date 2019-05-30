import pytest
from django.urls import reverse


@pytest.fixture
def client_lp_resp(client_with_lead):
    return client_with_lead.get(reverse('payments:client_landing_page'), secure=True)


def test_non_logged_status_code(client_lp_resp):
    assert client_lp_resp.status_code == 200
