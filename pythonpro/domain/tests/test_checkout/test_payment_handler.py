import pytest
from django_pagarme import facade
from django_pagarme.models import PagarmePayment, PagarmeNotification, PagarmeItemConfig
from model_bakery import baker

from pythonpro.cohorts.models import Cohort
from pythonpro.domain import checkout_domain
from pythonpro.memberkit import api
from pythonpro.memberkit.models import SubscriptionType, Subscription, PaymentItemConfigToSubscriptionType


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.checkout_domain.email_marketing_facade.tag_as.delay')


@pytest.fixture
def remove_tags_mock(mocker):
    return mocker.patch('pythonpro.domain.checkout_domain.email_marketing_facade.remove_tags.delay')


@pytest.fixture
def send_purchase_notification_mock(mocker):
    return mocker.patch('pythonpro.domain.checkout_domain.send_purchase_notification.delay')


def test_pagarme_payment_paid_boleto(db, tag_as_mock, remove_tags_mock, logged_user,
                                     send_purchase_notification_mock, mock_subscription_creation):
    payment = baker.make(PagarmePayment, payment_method=facade.BOLETO, user=logged_user)
    baker.make(PagarmeNotification, status=facade.PAID, payment=payment)
    config = baker.make(PagarmeItemConfig, payments=[payment])
    subscription_type = baker.make(SubscriptionType)
    PaymentItemConfigToSubscriptionType.objects.create(payment_item=config, subscription_type=subscription_type)

    checkout_domain.payment_handler_task(payment.id)
    assert tag_as_mock.called is False
    remove_tags_mock.assert_called_once_with(
        logged_user.email, logged_user.id, f'{config.slug}-boleto', f'{config.slug}-refused'
    )
    send_purchase_notification_mock.asser_called_once_with(payment.id)


@pytest.fixture
def api_key():
    key = 'some_key'
    api.set_default_api_key(key)
    return key


@pytest.fixture(autouse=True)
def enable_memberkit(settings):
    settings.MEMBERKIT_ON = True


@pytest.fixture
def mock_email_marketing_facade(mocker):
    return mocker.patch(
        'pythonpro.domain.subscription_domain.email_marketing_facade.create_or_update_user.delay'
    )


def test_subscription_creation(db, tag_as_mock, remove_tags_mock, logged_user,
                               send_purchase_notification_mock, responses, api_key, mock_email_marketing_facade):
    payment = baker.make(PagarmePayment, payment_method=facade.BOLETO, user=logged_user)
    cohort = baker.make(Cohort)
    baker.make(PagarmeNotification, status=facade.PAID, payment=payment)
    config = baker.make(PagarmeItemConfig, payments=[payment])
    subscription_type = baker.make(SubscriptionType, include_on_cohort=True, days_of_access=365)
    PaymentItemConfigToSubscriptionType.objects.create(payment_item=config, subscription_type=subscription_type)
    user_response = {
        'bio': None,
        'blocked': False,
        'email': logged_user.email,
        'enrollments': [],
        'full_name': logged_user.get_full_name(),
        'id': 1,
        'memberships': [
            {
                'expire_date': '2200-01-01',
                'membership_level_id': 4424,
                'status': 'active'
            }
        ],
        'profile_image_url': None,
        'unlimited': True
    }
    responses.add(
        responses.POST,
        f'https://memberkit.com.br/api/v1/users?api_key={api_key}',
    )
    responses.add(
        responses.GET,
        f'https://memberkit.com.br/api/v1/users/{logged_user.email}?api_key={api_key}',
        json=user_response
    )
    checkout_domain.payment_handler_task(payment.id)
    subscription = Subscription.objects.first()
    assert subscription is not None
    assert subscription.subscriber_id == payment.user_id
    assert subscription.status == Subscription.Status.ACTIVE
    assert subscription.payment_id == payment.id
    assert list(subscription.subscription_types.all()) == [subscription_type]
    assert subscription.responsible is None
    assert 'Criação como resposta de pagamento no Pagarme' in subscription.observation
    assert cohort.students.filter(id=logged_user.id).exists()
    assert mock_email_marketing_facade.call_count == 1


@pytest.fixture
def mock_subscription_creation(mocker):
    return mocker.patch(
        'pythonpro.domain.checkout_domain.subscription_domain.create_subscription_and_activate_services')


def test_pagarme_payment_paid_credit_card(mock_subscription_creation, db, tag_as_mock, remove_tags_mock,
                                          logged_user, send_purchase_notification_mock):
    payment = baker.make(PagarmePayment, payment_method=facade.CREDIT_CARD, user=logged_user)
    baker.make(PagarmeNotification, status=facade.PAID, payment=payment)
    config = baker.make(PagarmeItemConfig, payments=[payment])
    subscription_type = baker.make(SubscriptionType)
    PaymentItemConfigToSubscriptionType.objects.create(payment_item=config, subscription_type=subscription_type)
    checkout_domain.payment_handler_task(payment.id)
    assert tag_as_mock.called is False
    remove_tags_mock.assert_called_once_with(
        logged_user.email, logged_user.id, f'{config.slug}-refused'
    )
    send_purchase_notification_mock.asser_called_once_with(payment.id)


def test_pagarme_payment_waiting_payment_boleto(mock_subscription_creation, db, tag_as_mock, remove_tags_mock,
                                                logged_user, send_purchase_notification_mock):
    payment = baker.make(PagarmePayment, payment_method=facade.BOLETO, user=logged_user)
    baker.make(PagarmeNotification, status=facade.WAITING_PAYMENT, payment=payment)
    config = baker.make(PagarmeItemConfig, payments=[payment])
    checkout_domain.payment_handler_task(payment.id)
    assert remove_tags_mock.called is False
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, f'{config.slug}-boleto')
    send_purchase_notification_mock.asser_called_once_with(payment.id)


@pytest.mark.parametrize(
    'status',
    [
        facade.PROCESSING,
        facade.AUTHORIZED,
    ]
)
def test_pagarme_payment_with_item_but_do_nothing_status(db, tag_as_mock, remove_tags_mock, status):
    payment = baker.make(PagarmePayment)
    baker.make(PagarmeNotification, status=status, payment=payment)
    baker.make(PagarmeItemConfig, payments=[payment])
    checkout_domain.payment_handler_task(payment.id)
    assert tag_as_mock.called is False
    assert remove_tags_mock.called is False


@pytest.fixture
def inactivate_subscription_on_all_services(mocker):
    return mocker.patch(
        'pythonpro.domain.checkout_domain.subscription_domain.inactivate_subscription_on_all_services')


@pytest.mark.parametrize(
    'status',
    [
        facade.REFUNDED,
        facade.PENDING_REFUND,
    ]
)
def test_pagarme_subscription_inactivation(
        db, tag_as_mock, remove_tags_mock, status, inactivate_subscription_on_all_services):
    payment = baker.make(PagarmePayment)
    baker.make(PagarmeNotification, status=status, payment=payment)
    config = baker.make(PagarmeItemConfig, payments=[payment])
    subscription_type = baker.make(SubscriptionType)
    subscription = baker.make(Subscription, payment=payment)
    subscription.subscription_types.add(subscription_type)
    PaymentItemConfigToSubscriptionType.objects.create(payment_item=config, subscription_type=subscription_type)

    checkout_domain.payment_handler_task(payment.id)

    assert tag_as_mock.called is False
    assert remove_tags_mock.called is False
    inactivate_subscription_on_all_services.assert_called_once_with(subscription)


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
def test_pagarme_payment_absent_item(db, tag_as_mock, remove_tags_mock, status):
    payment = baker.make(PagarmePayment)
    baker.make(PagarmeNotification, status=status, payment=payment)
    checkout_domain.payment_handler_task(payment.id)
    assert tag_as_mock.called is False
    assert remove_tags_mock.called is False


def test_pagarme_payment_refused(db, tag_as_mock, remove_tags_mock, logged_user,
                                 send_purchase_notification_mock):
    payment = baker.make(PagarmePayment, user=logged_user)
    baker.make(PagarmeNotification, status=facade.REFUSED, payment=payment)
    config = baker.make(PagarmeItemConfig, payments=[payment])
    checkout_domain.payment_handler_task(payment.id)
    assert remove_tags_mock.called is False
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, f'{config.slug}-refused')
    send_purchase_notification_mock.asser_called_once_with(payment.id)
