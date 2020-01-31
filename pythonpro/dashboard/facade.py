from functools import partial
from itertools import chain, product
from operator import attrgetter

import pytz
from django.db.models import Count, Max, Sum
from django.utils.datetime_safe import datetime

from pythonpro.dashboard.models import TopicInteraction as _TopicInteracion
from pythonpro.modules.facade import get_entire_content_forest
from pythonpro.modules.models import Topic


def has_watched_any_topic(user) -> bool:
    return _TopicInteracion.objects.filter(user=user).exists()


def calculate_topic_interaction_history(user):
    """
    Calculate user's interaction history ordered by last topic interaction
    It will return a list of topics annotated with:
        1. last_interaction: last time user interacted with topic
        2. max_watched_time: max video time where user stopped watching
        3. total_watched_time: sum of all time user spent watching video
        4. interactions_count: number of times user started watching video
        5. duration: topic duration based on the min time this class had
    :param user:
    :return:
    """

    return Topic.objects.filter(
        topicinteraction__user=user
    ).annotate(
        last_interaction=Max('topicinteraction__creation'),
        max_watched_time=Max('topicinteraction__max_watched_time'),
        total_watched_time=Sum('topicinteraction__total_watched_time'),
        interactions_count=Count('topicinteraction')
    ).order_by('-last_interaction').select_related('chapter').select_related('chapter__section').select_related(
        'chapter__section__module')[:20]


def calculate_module_progresses(user):
    """
    Calculate the user progress on all modules
    :param user:
    :return:
    """
    # arbitrary default value for last interaction
    default_min_time = datetime(1970, 1, 1, tzinfo=pytz.utc)
    topic_property_defaults = {
        'last_interaction': default_min_time,
        'max_watched_time': 0,
        'total_watched_time': 0,
        'interactions_count': 0,
        'topics_count': 0,
        'finished_topics_count': 0,
    }

    # this is here due to bug on Heroku which is not installing Python 3.8:
    # https://sentry.io/organizations/python-pro/issues/1471675608/?project=236278&query=is%3Aunresolved
    def sum_with_start_0(lst):
        lst = list(lst)
        if len(lst) == 0:
            return 0
        return sum(lst)

    aggregation_functions = {
        'last_interaction': partial(max, default=default_min_time),
        'max_watched_time': sum_with_start_0,
        'total_watched_time': sum_with_start_0,
        'interactions_count': sum_with_start_0,
        'topics_count': sum_with_start_0,
        'finished_topics_count': sum_with_start_0,
        'duration': sum_with_start_0,
    }

    def _aggregate_statistics(contents, content_children_property_name):
        for content, (property_, aggregation_function) in product(contents, aggregation_functions.items()):
            children = getattr(content, content_children_property_name)
            setattr(content, property_, aggregation_function(map(attrgetter(property_), children)))

    def _flaten(iterable, children_property_name):
        for i in iterable:
            for child in getattr(i, children_property_name):
                yield child

    def calculate_progression(content):
        try:
            return min(content.max_watched_time / content.duration, 1)
        except ZeroDivisionError:
            return 0

    qs = Topic.objects.filter(topicinteraction__user=user).values('id').annotate(
        last_interaction=Max('topicinteraction__creation'),
        interactions_count=Max('topicinteraction'),
        max_watched_time=Max('topicinteraction__max_watched_time'),
        total_watched_time=Sum('topicinteraction__total_watched_time'),
        children_count=Count('topicinteraction')).all()

    user_interacted_topics = {t['id']: t for t in qs}
    modules = get_entire_content_forest()
    all_sections = list(_flaten(modules, 'sections'))
    all_chapters = list(_flaten(all_sections, 'chapters'))
    all_topics = list(_flaten(all_chapters, 'topics'))
    for topic, (property_, default_value) in product(all_topics, topic_property_defaults.items()):
        user_interaction_data = user_interacted_topics.get(topic.id, {})
        setattr(topic, property_, user_interaction_data.get(property_, default_value))
    for topic in all_topics:
        topic.progress = calculate_progression(topic)
        topic.topics_count = 1
        watched_to_end = topic.progress > 0.99
        spent_half_time_watching = topic.total_watched_time * 2 > topic.duration
        topic.finished_topics_count = 1 if (watched_to_end and spent_half_time_watching) else 0

    contents_with_children_property_name = [
        (all_chapters, 'topics'),
        (all_sections, 'chapters'),
        (modules, 'sections')
    ]
    for contents, content_children_property_name in contents_with_children_property_name:
        _aggregate_statistics(contents, content_children_property_name)

    for content in chain(all_chapters, all_sections, modules):
        setattr(content, 'progress', calculate_progression(content))

    return modules
