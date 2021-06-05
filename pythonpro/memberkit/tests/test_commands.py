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
    assert 2 == Subscription.objects.count()
