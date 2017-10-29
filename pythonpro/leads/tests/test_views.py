import pytest
from django.urls import reverse


@pytest.fixture()
def new_resp(client):
    return client.post(
        reverse('leads:new'),
        {
            'name': 'Renzo',
            'email': 'renzo@python.pro.br'
        }
    )


def test_new_lead_status(new_resp):
    assert 200 == new_resp.status_code
