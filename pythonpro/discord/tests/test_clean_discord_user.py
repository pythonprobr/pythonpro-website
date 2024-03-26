import pytest
from responses import matchers

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


discord_user_id = '1055109241507160165'


@pytest.fixture
def mock_discord_bot_msg_requests(responses, settings):
    channel_id = '122334232132323'
    responses.add(
        responses.POST, 'https://discord.com/api/v10/users/@me/channels', json={'id': channel_id}, status=200,
        match=[
            matchers.json_params_matcher({'recipient_id': discord_user_id})
        ]
    )
    responses.add(
        responses.POST, f'https://discord.com/api/v10/channels/{channel_id}/messages', json={'id': 'message_id'},
        status=200
    )
    responses.add(
        responses.DELETE, f'https://discord.com/api/v10/guilds/{settings.DISCORD_GUILD_ID}/members/{discord_user_id}',
        status=204
    )


def test_no_discord_user(db, mock_discord_bot_msg_requests):
    clean_discord_user(discord_user_id)
    user = DiscordLead.objects.get(discord_id=discord_user_id)
    assert user.status == DiscordLead.Status.INACTIVE


def test_subscription_inactive(db, mock_discord_bot_msg_requests):
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


def test_subscription_type_has_no_discord_access(db, mock_discord_bot_msg_requests):
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
