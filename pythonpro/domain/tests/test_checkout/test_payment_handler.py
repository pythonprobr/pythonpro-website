import pytest
from django_pagarme import facade
from django_pagarme.models import PagarmePayment, PagarmeNotification, PagarmeItemConfig
from model_mommy import mommy

from pythonpro.domain import checkout_domain


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.checkout_domain.email_marketing_facade.tag_as.delay')


@pytest.fixture
def remove_tags_mock(mocker):
    return mocker.patch('pythonpro.domain.checkout_domain.email_marketing_facade.remove_tags.delay')


@pytest.fixture
def promote_user_mock(mocker, logged_user):
    return mocker.patch('pythonpro.domain.checkout_domain._promote')


def test_pagarme_payment_paid_boleto(db, tag_as_mock, remove_tags_mock, promote_user_mock, logged_user):
    payment = mommy.make(PagarmePayment, payment_method=facade.BOLETO, user=logged_user)
    mommy.make(PagarmeNotification, status=facade.PAID, payment=payment)
    config = mommy.make(PagarmeItemConfig, payments=[payment])
    checkout_domain.payment_handler_task(payment.id)
    assert tag_as_mock.called is False
    remove_tags_mock.assert_called_once_with(logged_user.email, logged_user.id, f'{config.slug}-boleto')
    promote_user_mock.assert_called_once_with(logged_user, config.slug)


def test_pagarme_payment_paid_credit_card(db, tag_as_mock, remove_tags_mock, promote_user_mock, logged_user):
    payment = mommy.make(PagarmePayment, payment_method=facade.CREDIT_CARD, user=logged_user)
    mommy.make(PagarmeNotification, status=facade.PAID, payment=payment)
    config = mommy.make(PagarmeItemConfig, payments=[payment])
    checkout_domain.payment_handler_task(payment.id)
    assert tag_as_mock.called is False
    assert remove_tags_mock.called is False
    promote_user_mock.assert_called_once_with(logged_user, config.slug)


def test_pagarme_payment_waiting_payment_boleto(db, tag_as_mock, remove_tags_mock, promote_user_mock, logged_user):
    payment = mommy.make(PagarmePayment, payment_method=facade.BOLETO, user=logged_user)
    mommy.make(PagarmeNotification, status=facade.WAITING_PAYMENT, payment=payment)
    config = mommy.make(PagarmeItemConfig, payments=[payment])
    checkout_domain.payment_handler_task(payment.id)
    assert remove_tags_mock.called is False
    assert promote_user_mock.called is False
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, f'{config.slug}-boleto')


@pytest.mark.parametrize(
    'status',
    [
        facade.PROCESSING,
        facade.AUTHORIZED,
        facade.REFUNDED,
        facade.PENDING_REFUND,
        facade.REFUSED,
    ]
)
def test_pagarme_payment_with_item_but_do_nothing_status(db, tag_as_mock, remove_tags_mock, promote_user_mock, status):
    payment = mommy.make(PagarmePayment)
    mommy.make(PagarmeNotification, status=status, payment=payment)
    mommy.make(PagarmeItemConfig, payments=[payment])
    checkout_domain.payment_handler_task(payment.id)
    assert tag_as_mock.called is False
    assert remove_tags_mock.called is False
    assert promote_user_mock.called is False


@pytest.mark.parametrize(
    'status',
    [
        facade.PROCESSING,
        facade.AUTHORIZED,
        facade.PAID,
        facade.REFUNDED,
        facade.PENDING_REFUND,
        facade.WAITING_PAYMENT,
        facade.REFUSED,
    ]
)
def test_pagarme_payment_absent_item(db, tag_as_mock, remove_tags_mock, promote_user_mock, status):
    payment = mommy.make(PagarmePayment)
    mommy.make(PagarmeNotification, status=status, payment=payment)
    checkout_domain.payment_handler_task(payment.id)
    assert tag_as_mock.called is False
    assert remove_tags_mock.called is False
    assert promote_user_mock.called is False
