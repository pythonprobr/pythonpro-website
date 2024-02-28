import logging

from celery import shared_task

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

    logging.info(f'Clean discord user: {discord_user_id} with status: {lead_status.label}')
