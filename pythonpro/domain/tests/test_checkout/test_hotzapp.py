import pytest
import responses
from django_pagarme import facade
from django_pagarme.models import PagarmePayment, PagarmeNotification, UserPaymentProfile
from model_bakery import baker

from pythonpro.domain.hotzapp_domain import verify_purchase, send_purchase_notification

succes_body = 'ok_5f24555e4dec7f1927bddddb'


@pytest.fixture
def resp_success_mock(settings):
    with responses.RequestsMock() as r:
        r.add(
            r.POST,
            settings.HOTZAPP_API_URL,
            body=succes_body,
            status=200
        )
        yield r


def test_verify_purchase_not_existing_user(active_product_item, resp_success_mock):
    resp = verify_purchase(name='User test', email='asser@test.com', phone=5563432343,
                           payment_item_slug=active_product_item.slug)
    assert resp.status_code == 200


@pytest.fixture
def payment_profile(logged_user):
    return baker.make(UserPaymentProfile, user=logged_user, email=logged_user.email, phone='12999999999')


@pytest.fixture(params=[facade.CREDIT_CARD, facade.BOLETO])
def payment(logged_user, active_product_item, payment_profile, request):
    return baker.make(
        PagarmePayment, payment_method=request.param, user=logged_user, items=[active_product_item]
    )


@pytest.fixture(params=[facade.REFUSED, facade.PAID, facade.WAITING_PAYMENT])
def pagarme_notification(payment, request):
    return baker.make(PagarmeNotification, status=request.param, payment=payment)


def test_send_purchase_notification(payment, pagarme_notification, resp_success_mock):
    resp = send_purchase_notification(payment.id)
    assert resp.status_code == 200


@pytest.fixture(params=[facade.REFUSED, facade.WAITING_PAYMENT])
def pagarme_notification_not_paid(payment, request):
    return baker.make(PagarmeNotification, status=request.param, payment=payment)


def test_verify_purchase_existing_user(active_product_item, resp_success_mock, payment_profile,
                                       pagarme_notification_not_paid):
    resp = verify_purchase(name=payment_profile.name, email=payment_profile.email,
                           phone=str(payment_profile.phone),
                           payment_item_slug=active_product_item.slug)
    assert resp.status_code == 200


@pytest.fixture
def pagarme_notification_paid(payment):
    return baker.make(PagarmeNotification, status=facade.PAID, payment=payment)


def test_dont_verify_purchase_existing_user_paid_before_30_minutes(active_product_item, payment_profile,
                                                                   pagarme_notification_paid, logged_user):
    with responses.RequestsMock():
        verify_purchase(name=payment_profile.name, email=payment_profile.email,
                        phone=str(payment_profile.phone),
                        payment_item_slug=active_product_item.slug)
