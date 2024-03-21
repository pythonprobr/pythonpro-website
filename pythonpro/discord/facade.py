import logging

from django.conf import settings

from pythonpro.discord.bot import discord_bot_client
from pythonpro.discord.tasks import clean_discord_user

logger = logging.getLogger(__name__)


def clean_discord_users():
    discord_user_id = 0
    while True:
        discord_members = discord_bot_client.list_guild_members(settings.DISCORD_GUILD_ID, after=discord_user_id)
        if len(discord_members) == 0:
            break
        for member in discord_members:
            discord_user = member['user']
            discord_user_id = discord_user['id']
            is_bot = discord_user.get('bot', False)
            if is_bot:
                continue
            logger.info(f'Scheduling Cleaning discord user with id {discord_user_id}')
            clean_discord_user.delay(discord_user_id)
