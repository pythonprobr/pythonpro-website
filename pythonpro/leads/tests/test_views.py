import pytest
from django.urls import reverse

from pythonpro.leads.models import Lead


@pytest.fixture()
def new_resp(client):
    return client.post(
        reverse('leads:new'),
        {
            'name': 'Renzo',
            'email': 'renzo@python.pro.br'
        }
    )


@pytest.mark.django_db(transaction=True)
def test_new_lead_status(new_resp):
    assert 302 == new_resp.status_code


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("new_resp")
def test_saved_lead():
    assert Lead.objects.exists()
