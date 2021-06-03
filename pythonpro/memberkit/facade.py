from typing import List

from pythonpro.memberkit import api
from pythonpro.memberkit.models import SubscriptionType


def synchronize_subscription_types() -> List[SubscriptionType]:
    return [
        SubscriptionType.objects.update_or_create(id=dct['id'], name=dct['name'])[0]
        for dct in api.list_membership_levels()
    ]
