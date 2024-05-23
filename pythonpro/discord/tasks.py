import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model

from pythonpro.discord.bot import devpro_discord_bot_client
from pythonpro.discord.models import DiscordLead, DiscordUser
from pythonpro.memberkit.models import Subscription

logger = logging.getLogger(__name__)

msg = """Olá, sou o bot da DevPro no Discord.

Eu não identifiquei sua conta de Discord em nosso sistema. Por isso eu removi seu acesso.

Você pode conferir todo seus histórico de assinaturas acessando

https://painel.dev.pro.br

Se tiver qualquer dúvida, entre em contato pelo email suporte@dev.pro.br

Um abraço do Bot da DevPro
"""


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
        devpro_discord_bot_client.send_user_message(discord_user_id, msg)
        devpro_discord_bot_client.remove_guild_member(settings.DISCORD_GUILD_ID, discord_user_id)

    logging.info(f'Clean discord user: {discord_user_id} with status: {lead_status.label}')


_SALES_MSG_TEMPLATE = """Usuário: {user_name}
Com licença expirando em {expiration_date}
Id: {user_id}
email; {user_email}
"""


_WARN_USER_TEMPLATE = """Olá {user_name},

Sua assinatura anual da DevPro está prestes a expirar, e queremos oferecer uma oportunidade imperdível para que você continue aproveitando todos os benefícios de ser nosso assinante. 

Renove agora e garanta um desconto exclusivo de R$ 300!

🔒 Por que renovar sua assinatura?

* Economize R$ 300: Apenas para assinantes atuais, estamos oferecendo um desconto especial de R$ 300 na renovação anual.
* Acesso Ininterrupto: Continue desfrutando de conteúdos exclusivos, cursos atualizados e suporte especializado sem nenhuma interrupção.
* Encontros ao Vivo com Instrutores Experientes: Mantenha o acesso a sessões ao vivo com nossos instrutores especializados, proporcionando aprendizado personalizado e esclarecimento de dúvidas em tempo real.
* Novidades e Exclusividades: Esteja sempre à frente com as últimas novidades e ferramentas que a DevPro tem a oferecer.

⚠️ Atenção: Este desconto de R$ 300 é válido apenas até o vencimento da sua assinatura atual. Após {expiration_date}, o valor cheio será aplicado, e você perderá essa oferta especial.

Não deixe essa oportunidade escapar! Renove sua assinatura agora e continue sua jornada de aprendizado e crescimento profissional com a DevPro.

Para renovar, acesse https://painel.dev.pro.br/checkout/pagarme/renovacao-comunidade-devpro ou entre em contato com nosso suporte através do suporte@dev.pro.br.

Estamos ansiosos para continuar sendo parte do seu sucesso!

Atenciosamente,
Bot DevPro

OBS: Para você não correr os risco de perder essa oportunidade, vou te reenviar essa mensagem uma vez por dia.
"""  # noqa: E501 W291


@shared_task(
    rate_limit=1,
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=700,
    retry_jitter=True
)
def warn_subscription_expiration(user_id: int, expiration_date: str):
    user = get_user_model().objects.select_related('discorduser').get(id=user_id)
    devpro_discord_bot_client.send_to_sales_channel(_SALES_MSG_TEMPLATE.format(
        user_name=user.first_name,
        user_email=user.email,
        user_id=user_id,
        expiration_date=expiration_date,

    ))

    logging.info(f'Warn msg sent to sales discord channel for user with id {user_id}')
    try:
        discorduser = user.discorduser
    except DiscordUser.DoesNotExist:
        logger.info(f'No discord user found for user with id {user.id}')
    else:
        devpro_discord_bot_client.send_user_message(
            discorduser.discord_id,
            _WARN_USER_TEMPLATE.format(
                user_name=user.first_name,
                expiration_date=expiration_date
            )
        )
        logger.info(f'Subscription warn sent to user with id: {user.id}')
    return None
