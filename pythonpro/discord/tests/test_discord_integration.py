from django.urls import reverse
from model_bakery import baker

from pythonpro.discord.models import DiscordUser
from pythonpro.memberkit.models import SubscriptionType, Subscription


def test_user_added_to_discord_server(client_with_user, logged_user, mocker):
    mocker.patch(
        'pythonpro.discord.views.add_user_to_discord_server',
        return_value={'user': discord_user_api_response}
    )
    subscription_type = baker.make(SubscriptionType, has_discord_access=True)
    baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=logged_user,
        subscription_types=[subscription_type]
    )
    client_with_user.get(reverse('discord:autorize'), data={'code': 'xpto'})
    discord_user_id = discord_user_api_response['id']
    discord_user = DiscordUser.objects.get(discord_id=discord_user_id)
    assert discord_user.discord_email == discord_user_api_response['email']


def test_user_updated_to_discord_server(client_with_user, logged_user, mocker):
    mocker.patch(
        'pythonpro.discord.views.add_user_to_discord_server',
        return_value={'user': discord_user_api_response}
    )
    subscription_type = baker.make(SubscriptionType, has_discord_access=True)
    baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=logged_user,
        subscription_types=[subscription_type]
    )
    baker.make(DiscordUser, user=logged_user)
    client_with_user.get(reverse('discord:autorize'), data={'code': 'xpto'})
    discord_user_id = discord_user_api_response['id']
    discord_user = DiscordUser.objects.get(discord_id=discord_user_id)
    assert discord_user.discord_email == discord_user_api_response['email']


def test_user_with_inactive_subscription_not_added_to_discord_server(client_with_user, logged_user, mocker):
    subscription_type = baker.make(SubscriptionType, has_discord_access=True)
    baker.make(
        Subscription,
        status=Subscription.Status.INACTIVE,
        subscriber=logged_user,
        subscription_types=[subscription_type]
    )
    response = client_with_user.get(reverse('discord:autorize'), data={'code': 'xpto'})
    assert response.status_code == 403


def test_user_with_suscription_type_without_access_not_added_to_discord_server(client_with_user, logged_user, mocker):
    subscription_type = baker.make(SubscriptionType, has_discord_access=False)
    baker.make(
        Subscription,
        status=Subscription.Status.ACTIVE,
        subscriber=logged_user,
        subscription_types=[subscription_type]
    )
    response = client_with_user.get(reverse('discord:autorize'), data={'code': 'xpto'})
    assert response.status_code == 403


def test_user_without_subscription_access_not_added_to_discord_server(client_with_user, logged_user, mocker):
    response = client_with_user.get(reverse('discord:autorize'), data={'code': 'xpto'})
    assert response.status_code == 403


discord_user_api_response = {
    'id': '800764510645256242',
    'username': 'renzopro',
    'avatar': '824db4a9821e21f2609e03e5815c23c0',
    'avatar_decoration': None,
    'discriminator': '3978',
    'public_flags': 0,
    'flags': 0,
    'banner': None,
    'banner_color': None,
    'accent_color': None,
    'locale': 'pt-BR',
    'mfa_enabled': True,
    'email': 'renzo@dev.pro.br',
    'verified': True
}
