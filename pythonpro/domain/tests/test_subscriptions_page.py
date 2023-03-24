from datetime import datetime

import pytest
from django.urls import reverse
from model_bakery import baker

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.memberkit.models import Subscription, SubscriptionType


@pytest.fixture
def subscriptions(logged_user, topic):
    bootcamper = baker.make(
        SubscriptionType,
        name='Bootcamper'
    )
    fellow = baker.make(
        SubscriptionType,
        name='Comunidade DevPro'
    )
    return [
        baker.make(
            Subscription,
            subscriber=logged_user,
            activated_at=None,
            status=Subscription.Status.INACTIVE,
            subscription_types=[bootcamper]
        ),
        baker.make(
            Subscription,
            subscriber=logged_user,
            activated_at=datetime(2022, 12, 15),
            status=Subscription.Status.ACTIVE,
            subscription_types=[fellow]
        )
    ]


@pytest.fixture
def resp(client_with_lead, subscriptions):
    return client_with_lead.get(
        reverse('dashboard:home'),
        secure=True
    )


def test_status_code(resp):
    assert resp.status_code == 200


def test_subscription_name_is_present(resp, subscriptions):
    for sub in subscriptions:
        for sub_type in sub.subscription_types.all():
            dj_assert_contains(resp, sub_type.name)


def test_table_instructions(resp, topic):
    dj_assert_contains(resp, 'Confira suas assinaturas')
