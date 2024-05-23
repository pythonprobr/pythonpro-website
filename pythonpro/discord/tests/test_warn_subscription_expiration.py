from model_bakery import baker

from pythonpro.discord.models import DiscordUser
from pythonpro.discord.tasks import warn_subscription_expiration, _SALES_MSG_TEMPLATE


def test_warn_subscription_expiration(django_user_model, mocker):
    user = baker.make(django_user_model)
    send_to_sales_mock = mocker.patch(
        'pythonpro.discord.facade.devpro_discord_bot_client.send_to_sales_channel',
        return_value=[]
    )
    expiration_date = '23/05/2024'
    warn_subscription_expiration(user.id, expiration_date)
    send_to_sales_mock.assert_called_once_with(_SALES_MSG_TEMPLATE.format(
        user_name=user.first_name,
        user_email=user.email,
        user_id=user.id,
        expiration_date=expiration_date,

    ))


WARN_MSG = """Olá John,

Sua assinatura anual da DevPro está prestes a expirar, e queremos oferecer uma oportunidade imperdível para que você continue aproveitando todos os benefícios de ser nosso assinante. 

Renove agora e garanta um desconto exclusivo de R$ 300!

🔒 Por que renovar sua assinatura?

* Economize R$ 300: Apenas para assinantes atuais, estamos oferecendo um desconto especial de R$ 300 na renovação anual.
* Acesso Ininterrupto: Continue desfrutando de conteúdos exclusivos, cursos atualizados e suporte especializado sem nenhuma interrupção.
* Encontros ao Vivo com Instrutores Experientes: Mantenha o acesso a sessões ao vivo com nossos instrutores especializados, proporcionando aprendizado personalizado e esclarecimento de dúvidas em tempo real.
* Novidades e Exclusividades: Esteja sempre à frente com as últimas novidades e ferramentas que a DevPro tem a oferecer.

⚠️ Atenção: Este desconto de R$ 300 é válido apenas até o vencimento da sua assinatura atual. Após 23/05/2024, o valor cheio será aplicado, e você perderá essa oferta especial.

Não deixe essa oportunidade escapar! Renove sua assinatura agora e continue sua jornada de aprendizado e crescimento profissional com a DevPro.

Para renovar, acesse https://painel.dev.pro.br/checkout/pagarme/renovacao-comunidade-devpro ou entre em contato com nosso suporte através do suporte@dev.pro.br.

Estamos ansiosos para continuar sendo parte do seu sucesso!

Atenciosamente,
Bot DevPro

OBS: Para você não correr os risco de perder essa oportunidade, vou te reenviar essa mensagem uma vez por dia.
"""  # noqa: E501 W291


def test_warn_subscription_expiration_user_and_sales_channel(django_user_model, mocker):
    django_user = baker.make(django_user_model, first_name='John')
    discord_user = baker.make(DiscordUser, user=django_user, discord_id='946364767864504360')

    send_to_sales_mock = mocker.patch(
        'pythonpro.discord.facade.devpro_discord_bot_client.send_to_sales_channel',
        return_value=[]
    )

    send_user_msg_mock = mocker.patch(
        'pythonpro.discord.facade.devpro_discord_bot_client.send_user_message',
        return_value=[]
    )
    expiration_date = '23/05/2024'

    warn_subscription_expiration(django_user.id, expiration_date)

    send_to_sales_mock.assert_called_once_with(_SALES_MSG_TEMPLATE.format(
        user_name=django_user.first_name,
        user_email=django_user.email,
        user_id=django_user.id,
        expiration_date=expiration_date,

    ))

    send_user_msg_mock.assert_called_once_with(discord_user.discord_id, WARN_MSG)
