from django.core import management
from django_pagarme import facade as pagarme_facade
from django_pagarme.models import PagarmePayment, PagarmeItemConfig, PagarmeNotification
from model_bakery import baker

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
