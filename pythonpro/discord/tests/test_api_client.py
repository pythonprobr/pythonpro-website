import pytest
from responses import matchers

from pythonpro.discord.api_client import DiscordCredentials, DiscordAppClient, DiscordAppAndBotClient, DiscordBotClient, UnathorizedOperation


def test_discord_credentials_generate_app_client(responses):
    app_client_id = '1004541875954405436'
    secret = 'Z5G0I747OrbYWugQRHfUgtcazuC6ArT5'
    redirect_url = 'http://localhost:8000/discord/autorize'
    discord_credentials = DiscordCredentials(
        app_client_id,
        secret,
        redirect_url
    )
    authorization_code = 'authorization_code'
    credentials_data = {
        'client_id': app_client_id,
        'client_secret': secret,
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_url
    }

    responses.add(
        responses.POST, 'https://discord.com/api/v10/oauth2/token', json=valid_response, status=200,

        match=[
            matchers.header_matcher({'Content-Type': 'application/x-www-form-urlencoded'}),
            matchers.urlencoded_params_matcher(credentials_data)
        ]
    )

    client = discord_credentials.generate_api_client(authorization_code)
    assert isinstance(client, DiscordAppClient)


def test_discord_credentials_generate_app_and_bot_client(responses):
    app_client_id = '1004541875954405436'
    secret = 'Z5G0I747OrbYWugQRHfUgtcazuC6ArT5'
    redirect_url = 'http://localhost:8000/discord/autorize'
    discord_credentials = DiscordCredentials(
        app_client_id,
        secret,
        redirect_url,
        'MTAwNDU0MTg3NTk1NDQwNTQzNg.GFcT5X.Kp4gVn0U1kOPvdwLku-oki7LI_wtbMma2E_ET4'
    )
    authorization_code = 'authorization_code'
    credentials_data = {
        'client_id': app_client_id,
        'client_secret': secret,
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_url
    }

    responses.add(
        responses.POST, 'https://discord.com/api/v10/oauth2/token', json=valid_response, status=200,
        match=[
            matchers.header_matcher({'Content-Type': 'application/x-www-form-urlencoded'}),
            matchers.urlencoded_params_matcher(credentials_data)
        ]
    )

    client = discord_credentials.generate_api_client(authorization_code)
    assert isinstance(client, DiscordAppAndBotClient)


def test_current_user(responses):
    access_token = 'access_token'
    client = DiscordAppClient(access_token)
    responses.add(
        responses.GET, 'https://discord.com/api/v10/users/@me', json=valid_user, status=200,
        match=[
            matchers.header_matcher({'Authorization': f'Bearer {access_token}'}),
        ]

    )
    assert client.current_user == valid_user


def test_current_user_in_cache(responses):
    access_token = 'access_token'
    client = DiscordAppClient(access_token)
    responses.add(
        responses.GET, 'https://discord.com/api/v10/users/@me', json=valid_user, status=200,
        match=[
            matchers.header_matcher({'Authorization': f'Bearer {access_token}'}),
        ]
    )

    first_current_user = client.current_user
    assert len(responses.calls) == 1
    second_current_user = client.current_user
    assert len(responses.calls) == 1
    assert first_current_user is second_current_user


def test_add_guild_member(responses):
    access_token = 'access_token'
    bot_token = 'MTAwNDU0MTg3NTk1NDQwNTQzNg.GFcT5X.Kp4gVn0U1kOPvdwLku-oki7LI_wtbMma2E_ET4'
    guild_id = 971162582624903288
    responses.add(
        responses.GET, 'https://discord.com/api/v10/users/@me', json=valid_user, status=200,
        match=[
            matchers.header_matcher({'Authorization': f'Bearer {access_token}'}),
        ]

    )

    user_id = valid_user['id']

    responses.add(
        responses.PUT,
        f'https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}',
        status=204,
        json={'user': valid_user},
        match=[
            matchers.header_matcher({'Authorization': f'Bot {bot_token}'}),
            matchers.json_params_matcher({'access_token': access_token})
        ]

    )
    client = DiscordAppAndBotClient(access_token, bot_token)
    member_data = client.add_guild_member(guild_id)

    assert len(member_data) == 1, 'can not have more data on response'
    assert member_data['user'] == valid_user


def test_remove_guild_member(responses):
    bot_token = 'MTAwNDU0MTg3NTk1NDQwNTQzNg.GFcT5X.Kp4gVn0U1kOPvdwLku-oki7LI_wtbMma2E_ET4'
    bot_client = DiscordBotClient(bot_token)
    guild_id = 971162582624903288
    user_id = 946364767864504360

    responses.add(
        responses.DELETE,
        f'https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}',
        status=204,
        match=[
            matchers.header_matcher({'Authorization': f'Bot {bot_token}'}),
        ]

    )

    bot_client.remove_guild_member(guild_id=guild_id, user_id=user_id)


def test_remove_guild_member_bot_missing_permissionts(responses):
    bot_token = 'MTAwNDU0MTg3NTk1NDQwNTQzNg.GFcT5X.Kp4gVn0U1kOPvdwLku-oki7LI_wtbMma2E_ET4'
    bot_client = DiscordBotClient(bot_token)
    guild_id = 971162582624903288
    user_id = 946364767864504360

    responses.add(
        responses.DELETE,
        f'https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}',
        status=403,
        json=unauthorized_kick_member_response,
        match=[
            matchers.header_matcher({'Authorization': f'Bot {bot_token}'}),
        ]

    )
    with pytest.raises(UnathorizedOperation):
        bot_client.remove_guild_member(guild_id=guild_id, user_id=user_id)


valid_response = {
    'access_token': 'wAQlcLIjxlaJLoI7DPyMkJec5qki6C',
    'expires_in': 604800,
    'refresh_token': 'etIsXsLnDdv65lfxqbtxndorPbWpvE',
    'scope': 'email', 'token_type': 'Bearer'
}

valid_user = {
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

unauthorized_kick_member_response = {'message': 'Missing Permissions', 'code': 50013}
