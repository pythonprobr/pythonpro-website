import logging

from celery import shared_task

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

    logging.info(f'Clean discord user: {discord_user_id} with status: {lead_status.label}')


msg = """Olá, sou o bot da DevPro no Discord.

Eu não identifiquei sua conta de Discord em nosso sistema. Então peço a gentileza de você conectar suas conta:

https://l.dev.pro.br/comunidade

Para fazer essa conexão você precisa ter uma assinatura com acesso ao discord Ativa.
Você pode conferir seu histórico de assinaturas aqui:

https://painel.dev.pro.br

Você pode renovar sua assinatura utilizando o link:

https://painel.dev.pro.br/checkout/pagarme/renovacao-comunidade-devpro

Na próxima semana, usuários sem assinatura ativa serão removidos do servidor do Discord.

Qualquer dúvida, mande mensagem no canal #suporte do servidor do Discord da DevPro:

https://discord.com/channels/971162582624903288/979392834308280380

Eu vou mandar essa mensagem novamente até o dia 26/03/2024. Depois dessa data, sua conta poderá ser removida.

Um abraço do Bot da DevPro
"""
