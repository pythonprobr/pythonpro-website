from django.conf import settings

from pythonpro.discord.api_client import DiscordBotClient

discord_bot_client = DiscordBotClient(settings.DISCORD_APP_BOT_TOKEN)
