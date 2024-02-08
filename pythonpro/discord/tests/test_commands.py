from django.core import management


def test_clean_discord_users_command(mocker):
    mocker.patch('pythonpro.discord.facade.discord_bot_client.list_guild_members', return_value=[])
    management.call_command('clean_discord_users')
