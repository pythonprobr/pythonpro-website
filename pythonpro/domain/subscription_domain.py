from json.decoder import JSONDecodeError

from celery import shared_task

from pythonpro.analytics.facade import posthog_alias
from pythonpro.email_marketing.facade import create_or_update_with_no_role

run_until_available = shared_task(autoretry_for=(JSONDecodeError,), retry_backoff=True, max_retries=None)


@run_until_available
def subscribe_with_no_role(session_id, name: str, email: str, *tags, id='0', phone=None):
    posthog_alias(session_id, email)
    return create_or_update_with_no_role(name, email, *tags, id=id, phone=phone)
