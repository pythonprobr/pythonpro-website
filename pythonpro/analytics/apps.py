import posthog
from django.apps import AppConfig
from django.conf import settings


class AnalyticsConfig(AppConfig):
    name = 'pythonpro.analytics'
    verbose_name = 'Analytics'

    def ready(self):
        posthog.api_key = settings.POSTHOG_API_KEY
        posthog.api_host = settings.POSTHOG_API_URL
