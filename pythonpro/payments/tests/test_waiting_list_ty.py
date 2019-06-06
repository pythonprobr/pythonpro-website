import pytest
from django.urls import reverse


@pytest.fixture
def subscription_closed(settings):
    settings.SUBSCRIPTIONS_OPEN = False


@pytest.fixture
def resp(subscription_closed, client_with_lead, logged_user, mocker):
    tag_as = mocker.patch('pythonpro.payments.views.tag_as')
    yield client_with_lead.get(reverse('payments:waiting_list_ty'), secure=True)
    tag_as.assert_called_once_with(logged_user.email, 'lista-de-espera')


def test_status_code(resp):
    assert resp.status_code == 200
