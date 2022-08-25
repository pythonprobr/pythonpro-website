from functools import cached_property
from typing import Union

import requests
from requests import HTTPError

_BASE_ENDPOINT_URI = 'https://discord.com/api/v10'


class MissingBotToken(Exception):
    def __init__(self) -> None:
        super().__init__('You need to provide the Bot Access Token into DiscordClient initialization')


class UnathorizedOperation(Exception):
    pass


class DiscordAppClient:
    def __init__(self, access_token: str):
        self._access_token = access_token

    @cached_property
    def current_user(self):
        headers = {
            'Authorization': f'Bearer {self._access_token}'
        }
        r = requests.get(f'{_BASE_ENDPOINT_URI}/users/@me', headers=headers)
        r.raise_for_status()
        discord_user_dict = r.json()
        return discord_user_dict


class DiscordBotClient:
    def __init__(self, bot_token: str):
        self._bot_token = bot_token

    def list_guild_members(self, guild_id, limit=1, after=0) -> dict:
        """
        :param guild_id: the discord server id
        """
        headers = {
            'Authorization': f'Bot {self._bot_token}'
        }
        data = {'limit': limit, 'after': after}
        r = requests.get(
            f'{_BASE_ENDPOINT_URI}/guilds/{guild_id}/members',
            # data=data,
            headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as error:
            if error.response.status_code == 403:
                raise UnathorizedOperation(
                    f"You have no permission to list member of Guild with id {guild_id}"
                    f"\nCheck if Guild id is right and you have added your Discord bot on Guild"
                ) from error
        else:
            return r.json()

    def remove_guild_member(self, guild_id, user_id):
        headers = {
            'Authorization': f'Bot {self._bot_token}'
        }
        r = requests.delete(
            f'{_BASE_ENDPOINT_URI}/guilds/{guild_id}/members/{user_id}',
            headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as error:
            if error.response.status_code == 403:
                raise UnathorizedOperation(
                    f"You have no permission to remove member {user_id} of Guild with id {guild_id}"
                    f"\nCheck if Guild id is right and you have added your Discord bot on Guild"
                    "\nAlso check that Bot has role bigger than the member you want to kick. Check more info on:"
                    "\nhttps://discord.com/developers/docs/topics/permissions#permission-hierarchy"
                ) from error


class DiscordAppAndBotClient(DiscordAppClient, DiscordBotClient):
    def __init__(self, access_token: str, bot_token: str):
        DiscordAppClient.__init__(self, access_token)
        DiscordBotClient.__init__(self, bot_token)

    def add_guild_member(self, guild_id) -> dict:
        """
        :param guild_id: the discord server id
        :return: a dict representing guild's member

        If user is already on guild, return a member dict but only with user data.
        """
        current_user = self.current_user
        headers = {
            'Authorization': f'Bot {self._bot_token}'
        }
        data = {'access_token': self._access_token}
        user_id = current_user['id']
        r = requests.put(
            f'{_BASE_ENDPOINT_URI}/guilds/{guild_id}/members/{user_id}',
            json=data,
            headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as error:
            if error.response.status_code == 403:
                raise UnathorizedOperation(
                    f"You have no permission to add user with id {user_id} on Guild if id {guild_id}"
                    f"\nCheck if Guild id is right and you have added your Discord bot on Guild"
                ) from error
        if r.status_code == 204:
            return {'user': current_user}
        elif r.status_code == 201:
            return r.json()


class DiscordCredentials:
    def __init__(self, app_client_id: str, app_client_secret: str, redirect_uri: str, bot_token=None):
        self._bot_token = bot_token
        self._app_client_id = app_client_id
        self._app_client_secret = app_client_secret
        self._redirect_uri = redirect_uri

    def generate_api_client(self, autorization_code: str) -> Union[DiscordAppClient, DiscordAppAndBotClient]:
        data = {
            'client_id': self._app_client_id,
            'client_secret': self._app_client_secret,
            'grant_type': 'authorization_code',
            'code': autorization_code,
            'redirect_uri': self._redirect_uri
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(f'{_BASE_ENDPOINT_URI}/oauth2/token', data=data, headers=headers)
        r.raise_for_status()
        oauth2_data = r.json()
        access_token = oauth2_data['access_token']
        if self._bot_token is None:
            return DiscordAppClient(access_token)
        return DiscordAppAndBotClient(access_token, self._bot_token)


if __name__ == '__main__':
    c = DiscordBotClient('MTAwNDU0MTg3NTk1NDQwNTQzNg.GFcT5X.Kp4gVn0U1kOPvdwLku-oki7LI_wtbMma2E_ET4')
    members = c.list_guild_members(971162582624903288)
    print(members)
