import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def subscription_closed(settings):
    settings.SUBSCRIPTIONS_OPEN = True


@pytest.fixture
def resp(subscription_closed, client_with_lead, mocker, logged_user):
    tag_as = mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as')
    yield client_with_lead.get(reverse('member_landing_page'), secure=True)
    tag_as.assert_called_once_with(logged_user.email, logged_user.id, 'potential-member')


def test_status_code(resp):
    assert resp.status_code == 200


@pytest.mark.parametrize(
    'url_name', [
        'payments:member_capture',
        'payments:member_checkout',
    ]
)
def test_checkout_link_is_present(resp, url_name):
    dj_assert_contains(resp, reverse(url_name))


def test_notification_link_is_present(resp, logged_user):
    dj_assert_contains(resp, reverse('payments:membership_notification', kwargs={'user_id': logged_user.id}))


def test_full_price(resp):
    dj_assert_contains(resp, '1599,90')
