from pythonpro.discord.models import DiscordLead, DiscordUser
from pythonpro.discord.tasks import clean_discord_user
from model_bakery import baker

from pythonpro.memberkit.models import SubscriptionType, Subscription


def test_active_user(db):
    discord_user_id = '1055109241507160165'
    django_user = baker.make(DiscordUser, discord_id=discord_user_id).user
    subscription_type = baker.make(SubscriptionType, has_discord_access=True)
    baker.make(
        Subscription,
        subscription_types=[subscription_type],
        subscriber=django_user,
        status=Subscription.Status.ACTIVE
    )
    clean_discord_user(discord_user_id)
    user = DiscordLead.objects.get(discord_id=discord_user_id)
    assert user.status == DiscordLead.Status.ACTIVE


def test_no_discord_user(db):
    discord_user_id = '1055109241507160165'
    clean_discord_user(discord_user_id)
    user = DiscordLead.objects.get(discord_id=discord_user_id)
    assert user.status == DiscordLead.Status.INACTIVE


def test_subscription_inactive(db):
    discord_user_id = '1055109241507160165'
    django_user = baker.make(DiscordUser, discord_id=discord_user_id).user
    subscription_type = baker.make(SubscriptionType, has_discord_access=True)
    baker.make(
        Subscription,
        subscription_types=[subscription_type],
        subscriber=django_user,
        status=Subscription.Status.INACTIVE
    )
    clean_discord_user(discord_user_id)
    user = DiscordLead.objects.get(discord_id=discord_user_id)
    assert user.status == DiscordLead.Status.INACTIVE


def test_subscription_type_has_no_discord_access(db):
    discord_user_id = '1055109241507160165'
    django_user = baker.make(DiscordUser, discord_id=discord_user_id).user
    subscription_type = baker.make(SubscriptionType, has_discord_access=False)
    baker.make(
        Subscription,
        subscription_types=[subscription_type],
        subscriber=django_user,
        status=Subscription.Status.ACTIVE
    )
    clean_discord_user(discord_user_id)
    user = DiscordLead.objects.get(discord_id=discord_user_id)
    assert user.status == DiscordLead.Status.INACTIVE
