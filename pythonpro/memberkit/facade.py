from typing import List

from pythonpro.memberkit import api
from pythonpro.memberkit.models import SubscriptionType, Subscription


def synchronize_subscription_types() -> List[SubscriptionType]:
    return [
        SubscriptionType.objects.update_or_create(id=dct['id'], name=dct['name'])[0]
        for dct in api.list_membership_levels()
    ]


def create_new_subscription(payment, observation: str = '') -> Subscription:
    subscription_types = [item.subscription_type_relation.subscription_type for item in payment.items.all()]
    if len(subscription_types) == 0:
        raise ValueError(f"Payment {payment} doesn't have subscription types")

    subscription = Subscription.objects.create(
        status=Subscription.Status.INACTIVE,
        payment=payment,
        subscriber=payment.user,
        observation=observation
    )
    subscription.subscription_types.set(subscription_types)
    return subscription
