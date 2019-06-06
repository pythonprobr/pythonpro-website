import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def subscription_closed(settings):
    settings.SUBSCRIPTIONS_OPEN = False


@pytest.fixture
def resp(subscription_closed, client_with_lead, mocker, logged_user):
    tag_as = mocker.patch('pythonpro.payments.views.tag_as')
    yield client_with_lead.get(reverse('payments:member_landing_page'), secure=True)
    tag_as.assert_called_once_with(logged_user.email, 'potential-member')


def test_status_code(resp):
    assert resp.status_code == 200


def test_subscription_link_is_present(resp):
    dj_assert_contains(resp, reverse('payments:waiting_list_ty'))
