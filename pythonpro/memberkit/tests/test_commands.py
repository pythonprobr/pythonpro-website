import pytest as pytest
from django.core import management
from django_pagarme import facade as pagarme_facade
from django_pagarme.models import PagarmePayment, PagarmeItemConfig, PagarmeNotification
from model_bakery import baker
from rolepermissions.roles import assign_role

from pythonpro.core.models import User
from pythonpro.memberkit.models import SubscriptionType, PaymentItemConfigToSubscriptionType, Subscription


def test_synchronize_paid_subscriptions(db):
    subscription_type = baker.make(SubscriptionType)
    payment_config = baker.make(PagarmeItemConfig)
    payment_to_subscription = PaymentItemConfigToSubscriptionType(
        payment_item=payment_config, subscription_type=subscription_type
    )
    payment_to_subscription.save()
    for status in pagarme_facade._impossible_states:
        # only one will have PAID status
        payment = baker.make(PagarmePayment, user=baker.make(User))
        payment.items.set([payment_config])
        baker.make(PagarmeNotification, payment=payment, status=status)

    payment = baker.make(PagarmePayment, user=baker.make(User))
    payment.items.set([payment_config])
    baker.make(PagarmeNotification, payment=payment, status=pagarme_facade.PAID)
    baker.make(PagarmeNotification, payment=payment, status=pagarme_facade.REFUNDED)
    management.call_command('synchronize_paid_subscriptions')
    assert 2 == Subscription.objects.filter(status=Subscription.Status.INACTIVE).count()


def test_fix_inactive_subscriptions(db):
    payment_config = baker.make(PagarmeItemConfig)
    inactive_with_paid_payment = _make_subscriptions_with_payment(payment_config, pagarme_facade.PAID)
    unpaid_statuses = set(pagarme_facade._impossible_states)
    unpaid_statuses.discard(pagarme_facade.PAID)
    for status in unpaid_statuses:
        # only one will have PAID status
        _make_subscriptions_with_payment(payment_config, status)

    # Make one refunded Subscription
    payment = baker.make(PagarmePayment, user=baker.make(User))
    payment.items.set([payment_config])
    baker.make(PagarmeNotification, payment=payment, status=pagarme_facade.PAID)
    baker.make(PagarmeNotification, payment=payment, status=pagarme_facade.REFUNDED)
    refunded_subscription = baker.make(Subscription, payment=payment, status=Subscription.Status.INACTIVE)

    # Make one subscriptions with no payment at all
    baker.make(Subscription, status=Subscription.Status.INACTIVE)
    active_without_payment = baker.make(Subscription, status=Subscription.Status.ACTIVE)

    active_with_paid_payment = _make_subscriptions_with_payment(payment_config, pagarme_facade.PAID)
    active_with_paid_payment.status = Subscription.Status.ACTIVE
    active_with_paid_payment.save()

    previous_subscriptions = Subscription.objects.count()
    assert 2 == Subscription.objects.filter(status=Subscription.Status.ACTIVE).count()

    management.call_command('fix_inactive_subscriptions')

    assert previous_subscriptions == Subscription.objects.count()
    assert 3 == Subscription.objects.filter(status=Subscription.Status.ACTIVE).count()
    assert not Subscription.objects.filter(status=Subscription.Status.ACTIVE, id=refunded_subscription.id).exists()

    appended_observation_message = '\n\nAtivada via comando automático do servidor.'
    active_without_payment.refresh_from_db()
    assert not active_without_payment.observation.endswith(appended_observation_message)
    active_with_paid_payment.refresh_from_db()
    assert not active_with_paid_payment.observation.endswith(appended_observation_message)
    inactive_with_paid_payment.refresh_from_db()
    assert inactive_with_paid_payment.observation.endswith(appended_observation_message)


def _make_subscriptions_with_payment(payment_config, status):
    payment = baker.make(PagarmePayment, user=baker.make(User))
    payment.items.set([payment_config])
    baker.make(PagarmeNotification, payment=payment, status=status)
    return baker.make(Subscription, payment=payment, status=Subscription.Status.INACTIVE)


@pytest.fixture
def subscription_types(db):
    role_to_subscription_type_dct = {
        'data_scientist': 4456,
        'webdev': 4426,
        'member': 4424,
        'bootcamper': 4423,
        'client': 4420,
    }
    return [
        baker.make(SubscriptionType, id=v, name=k)
        for k, v in role_to_subscription_type_dct.items()
    ]


def test_subscription_not_created_for_lead(django_user_model):
    lead = baker.make(django_user_model)
    assign_role(lead, 'lead')
    management.call_command('create_subscriptions_for_roles')
    assert not Subscription.objects.exists()


role_to_subscription = pytest.mark.parametrize(
    'role,subscription_type_id',
    [
        ('data_scientist', 4456),
        ('client', 4420),
        ('webdev', 4426),
        ('member', 4424),
        ('pythonista', 4423),
        ('bootcamper', 4423),
    ]
)


@role_to_subscription
def test_subscription_created(role, subscription_type_id, subscription_types, django_user_model):
    user_with_role = baker.make(django_user_model)
    assign_role(user_with_role, role)
    management.call_command('create_subscriptions_for_roles')
    subscription = Subscription.objects.first()
    assert subscription.subscriber == user_with_role
    assert subscription.status == Subscription.Status.INACTIVE
    assert subscription.subscription_types.first().id == subscription_type_id


@role_to_subscription
def test_subscription_creation_idempotence(role, subscription_type_id, subscription_types, django_user_model):
    user_with_role = baker.make(django_user_model)
    assign_role(user_with_role, role)
    previous_subscription = baker.make(Subscription, subscriber=user_with_role)
    previous_subscription.subscription_types.add(subscription_type_id)
    management.call_command('create_subscriptions_for_roles')
    management.call_command('create_subscriptions_for_roles')
    assert Subscription.objects.count() == 1, 'Subscription should not be created'


@pytest.mark.parametrize(
    'role,subscription_type_id',
    [
        ('data_scientist', 4424),
        ('client', 4424),
        ('webdev', 4424),
        ('member', 4420),
        ('pythonista', 4424),
        ('bootcamper', 4424),
    ]
)
def test_subscription_creation_another_subscription_type(role, subscription_type_id, subscription_types,
                                                         django_user_model):
    """
    Check all ids from parametrize area different from role_to_subscription
    :param role:
    :param subscription_type_id:
    :param subscription_types:
    :param django_user_model:
    :return:
    """
    user_with_role = baker.make(django_user_model)
    assign_role(user_with_role, role)
    previous_subscription = baker.make(Subscription, subscriber=user_with_role)
    previous_subscription.subscription_types.add(subscription_type_id)
    management.call_command('create_subscriptions_for_roles')
    assert Subscription.objects.count() == 2, 'New Subscription should be created'
    management.call_command('create_subscriptions_for_roles')
    assert Subscription.objects.count() == 2, 'New Subscription should be created only once'


def test_inactivate_expired_subscriptions(django_user_model, mocker):
    process_expired_subscriptions_mock = mocker.patch('pythonpro.memberkit.facade.process_expired_subscriptions.delay')
    active_user = baker.make(django_user_model)
    baker.make(Subscription, status=Subscription.Status.ACTIVE, subscriber=active_user)
    management.call_command('inactivate_expired_subscriptions')
    process_expired_subscriptions_mock.assert_called_once_with(active_user.id)
