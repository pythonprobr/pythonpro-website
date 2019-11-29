from pythonpro.dashboard.models import TopicInteraction as _TopicInteracion


def has_watched_any_topic(user) -> bool:
    return _TopicInteracion.objects.filter(user=user).exists()
