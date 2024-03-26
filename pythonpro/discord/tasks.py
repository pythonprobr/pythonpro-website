import logging

from celery import shared_task
from django.conf import settings

from pythonpro.discord.bot import discord_bot_client
from pythonpro.discord.models import DiscordLead
from pythonpro.memberkit.models import Subscription

logger = logging.getLogger(__name__)


@shared_task(
    rate_limit=1,
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=700,
    retry_jitter=True
)
def clean_discord_user(discord_user_id):
    has_discord_access = Subscription.objects.filter(
        status=Subscription.Status.ACTIVE,
        subscription_types__has_discord_access=True,
        subscriber__discorduser__discord_id=discord_user_id
    ).exists()

    lead_status = DiscordLead.Status.ACTIVE if has_discord_access else DiscordLead.Status.INACTIVE
    DiscordLead.objects.update_or_create(
        defaults={'status': lead_status},
        discord_id=discord_user_id
    )

    if not has_discord_access:
        dm_channel = discord_bot_client.get_dm_channel(discord_user_id)
        discord_bot_client.create_message(dm_channel['id'], msg)
        discord_bot_client.remove_guild_member(settings.DISCORD_GUILD_ID, discord_user_id)

    logging.info(f'Clean discord user: {discord_user_id} with status: {lead_status.label}')


msg = """Olá, sou o bot da DevPro no Discord.

Eu não identifiquei sua conta de Discord em nosso sistema. Por isso eu removi seu acesso.

Você pode conferir todo seus histórico de assinaturas acessando

https://painel.dev.pro.br

Se tiver qualquer dúvida, entre em contato pelo email suporte@dev.pro.br

Um abraço do Bot da DevPro
"""
