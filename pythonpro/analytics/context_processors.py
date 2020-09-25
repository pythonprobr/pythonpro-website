from django.conf import settings


def posthog_configurations(request):
    return {
        'POSTHOG_API_KEY': settings.POSTHOG_API_KEY,
        'POSTHOG_API_URL': settings.POSTHOG_API_URL,
    }
