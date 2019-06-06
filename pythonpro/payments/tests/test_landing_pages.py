import pytest
from django.urls import reverse


@pytest.fixture
def client_lp_resp(client_with_lead, mocker, logged_user):
    tag_as = mocker.patch('pythonpro.payments.views.tag_as')
    yield client_with_lead.get(reverse('payments:client_landing_page'), secure=True)
    tag_as.assert_called_once_with(logged_user.email, 'potential-client')


def test_non_logged_status_code(client_lp_resp):
    assert client_lp_resp.status_code == 200
