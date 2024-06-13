from django.conf import settings

from pythonpro.discord.api_client import DiscordBotClient


class _DevProDiscordBotClient(DiscordBotClient):
    """
    This class provides data respective to specific seetings for DevPro Discord Guild
    """

    def send_to_sales_channel(self, msg: str) -> dict:
        return self.create_message(settings.DISCORD_GUILD_SALES_CHANNEL_ID, msg)

    def send_to_checkout_channel(self, msg: str) -> dict:
        return self.create_message(settings.DISCORD_GUILD_SALES_CHANNEL_ID, msg)


devpro_discord_bot_client = _DevProDiscordBotClient(settings.DISCORD_APP_BOT_TOKEN)
