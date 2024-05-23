import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Max

from pythonpro.discord.bot import devpro_discord_bot_client
from pythonpro.discord.tasks import clean_discord_user, warn_subscription_expiration
from pythonpro.memberkit.models import Subscription

from django.utils.timezone import datetime

logger = logging.getLogger(__name__)


def clean_discord_users():
    discord_user_id = 0
    while True:
        discord_members = devpro_discord_bot_client.list_guild_members(settings.DISCORD_GUILD_ID, after=discord_user_id)
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


def warn_users_about_subscription_expiration():
    today = datetime.today()
    thirty_days_in_future = today + timedelta(days=30)
    users_with_subscription_expirating = get_user_model().objects.annotate(
        max_subscription_expiration_date=Max('subscriptions__expired_at')
    ).filter(
        subscriptions__status=Subscription.Status.ACTIVE,
        max_subscription_expiration_date__lte=thirty_days_in_future
    ).values('id', 'max_subscription_expiration_date')
    for user_dct in users_with_subscription_expirating:
        warn_subscription_expiration.delay(
            user_dct['id'],
            user_dct['max_subscription_expiration_date'].strftime('%d/%m/%Y')
        )
