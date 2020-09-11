"""
Domain responsible for calculate content statistics in general
"""
from functools import partial
from itertools import chain, product
from operator import attrgetter

import pytz
from celery import shared_task
from django.db.models import Count, Max, Sum
from django.utils.datetime_safe import datetime

from pythonpro.core import facade as core_facade
from pythonpro.dashboard.models import TopicInteraction
from pythonpro.email_marketing import facade as email_marketing_facade
from pythonpro.modules.facade import (
    get_entire_content_forest,
    get_topic_with_contents_by_id,
    get_tree,
    topics_user_interacted_queryset,
    get_tree_by_module_slug,
)

__all = [
    'calculate_topic_interaction_history',
    'calculate_module_progresses'
]


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
    :return: Topic annotated with statistics
    """

    return topics_user_interacted_queryset(user).annotate(
        last_interaction=Max('topicinteraction__creation'),
        max_watched_time=Max('topicinteraction__max_watched_time'),
        total_watched_time=Sum('topicinteraction__total_watched_time'),
        interactions_count=Count('topicinteraction')
    ).order_by('-last_interaction')[:20]


def calculate_modules_progresses(user):
    """
    Calculate the user progress on all modules
    :param user:
    :return:
    """
    modules = get_entire_content_forest()
    return _calculate_modules_statistics(modules, user)


def calculate_module_progresses_using_slug(user, module_slug):
    """
    Calculate the user progress on this module
    :param module_slug: Module slug progresses will be calculated
    :param user:
    :return:
    """

    module = get_tree_by_module_slug(module_slug)
    return _calculate_modules_statistics([module], user)[0]


def calculate_module_progresses(user, module):
    """
    Calculate the user progress on this module
    :param module: Module progresses will be calculated
    :param user:
    :return:
    """
    module.sections = get_tree(module)
    return _calculate_modules_statistics([module], user)[0]


def _calculate_modules_statistics(modules, user):
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

    qs = TopicInteraction.objects.filter(user=user).values('topic_id').annotate(
        last_interaction=Max('creation'),
        interactions_count=Count('*'),
        max_watched_time=Max('max_watched_time'),
        total_watched_time=Sum('total_watched_time')
    ).all()
    user_interacted_topics = {t['topic_id']: t for t in qs}
    all_sections = list(_flaten(modules, 'sections'))
    all_chapters = list(_flaten(all_sections, 'chapters'))
    all_topics = list(_flaten(all_chapters, 'topics'))
    for topic, (property_, default_value) in product(all_topics, topic_property_defaults.items()):
        user_interaction_data = user_interacted_topics.get(topic.id, {})
        setattr(topic, property_, user_interaction_data.get(property_, default_value))
    for topic in all_topics:
        topic.progress = calculate_progression(topic)
        topic.topics_count = 1
        watched_to_end = topic.progress >= 0.8
        spent_half_time_watching = topic.total_watched_time * 3 >= topic.duration
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


def _generate_completed_contents(modules):
    for module in modules:
        if _is_completed(module):
            yield module
        for section in module.sections:
            if _is_completed(section):
                yield section
            for chapter in section.chapters:
                if _is_completed(chapter):
                    yield chapter
                for topic in chapter.topics:
                    if _is_completed(topic):
                        yield topic


def completed_contents(user):
    """
    Calculate a list with all contents (Module, Section, Chapter or Topic) user has completed
    :param user:
    :return: generator of completed contents
    """
    modules = calculate_modules_progresses(user)
    yield from _generate_completed_contents(modules)


def completed_module_contents(user, module):
    """
    Calculate a list with all contents (Module, Section, Chapter or Topic) user has completed
    :param user:
    :return: generator of completed contents
    """
    module_progresses = calculate_module_progresses(user, module)
    yield from _generate_completed_contents([module_progresses])


def _is_completed(content):
    return content.topics_count > 0 and (content.finished_topics_count == content.topics_count)


@shared_task()
def tag_newly_completed_contents(user_or_user_id, topic_id: int):
    """
    Tag user completed contents on email marketing for segmentation
    This will only consider module -> section -> chapter -> topic
    accordingly with topics_id
    :param topic_id: topic_id from topic user last updated
    :param user_or_user_id: Django User or his id
    :return: list of contents_full_tags
    """
    user = core_facade.find_user_by_id(user_or_user_id)
    topic = get_topic_with_contents_by_id(topic_id)
    possible_changing_tags = {
        topic.chapter.section.module.full_slug,
        topic.chapter.section.full_slug,
        topic.chapter.full_slug,
        topic.full_slug,
    }
    completed_module_content_slugs = (c.full_slug for c in completed_module_contents(user, topic.find_module()))
    tags = [s for s in completed_module_content_slugs if s in possible_changing_tags]
    if tags:
        email_marketing_facade.tag_as(user.email, user.id, *tags)
    return tags
