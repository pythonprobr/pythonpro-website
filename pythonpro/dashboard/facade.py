from pythonpro.dashboard.models import TopicInteraction

__all__ = ['has_watched_any_topic', ]


def has_watched_any_topic(user) -> bool:
    """
    Indicates if a user has watched any topic
    :param: user
    :return: boolean
    """
    return TopicInteraction.objects.filter(user=user).exists()
