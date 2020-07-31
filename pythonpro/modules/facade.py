from functools import partial

from django.conf import settings
from django.core.cache import cache
from django.db.models import Prefetch

from pythonpro.modules.models import (
    Chapter as _Chapter, Module as _Module, Section as _Section, Topic as _Topic,
)


def get_topic_model():
    return _Topic


def get_all_modules():
    """
    Search all modules on database sorted by order
    :return: tuple of Module
    """
    lazy_all_modules = partial(tuple, _Module.objects.order_by('order'))
    return cache.get_or_set('ALL_MODULES', lazy_all_modules, settings.CACHE_TTL)


def get_module_with_contents(slug):
    """
    Search for a module with respective sections and chapters
    :param slug: module's slug
    :return: Module with respective section on attribute sections
    """

    return _Module.objects.filter(slug=slug).prefetch_related(
        Prefetch(
            'section_set',
            queryset=_Section.objects.order_by('order').prefetch_related(
                Prefetch(
                    'chapter_set',
                    queryset=_Chapter.objects.order_by('order'),
                    to_attr='chapters'
                )
            ),
            to_attr='sections')
    ).get()


def get_section_with_contents(slug):
    """
    Search for a section with respective module and chapters
    :param slug: section's slug
    :return: Section
    """
    return _Section.objects.filter(slug=slug).select_related('module').prefetch_related(
        Prefetch(
            'chapter_set',
            queryset=_Chapter.objects.order_by('order'),
            to_attr='chapters'
        )
    ).get()


def get_chapter_with_contents(slug):
    """
    Search for a chapter respective to slug with it's module, section and topics
    :param slug: chapter's slug
    :return: Chapter
    """
    return _Chapter.objects.filter(slug=slug).select_related('section').select_related(
        'section__module').prefetch_related(
        Prefetch(
            'topic_set',
            queryset=_Topic.objects.order_by('order'),
            to_attr='topics'
        )).get()


def get_topic_with_contents(slug):
    """
    Search for a topic respective to slug with it's module, section and chapter
    :param slug: topic's slug
    :return: Topic
    """
    return _Topic.objects.filter(slug=slug).select_related('chapter').select_related('chapter__section').select_related(
        'chapter__section__module').get()


def get_topic_with_contents_by_id(id: int) -> _Topic:
    """
    Search for a topic respective to slug with it's module, section and chapter
    :param id: topic's id
    :return: Topic
    """
    return _Topic.objects.filter(id=id).select_related('chapter').select_related('chapter__section').select_related(
        'chapter__section__module').get()


def get_entire_content_forest():
    """
    Return a list of modules with the entire content on it
    :return:
    """
    return list(_Module.objects.all().prefetch_related(
        Prefetch(
            'section_set',
            queryset=_Section.objects.order_by('order').prefetch_related(
                Prefetch(
                    'chapter_set',
                    queryset=_Chapter.objects.order_by('order').prefetch_related(
                        Prefetch(
                            'topic_set',
                            queryset=_Topic.objects.order_by('order'),
                            to_attr='topics'
                        )
                    ),
                    to_attr='chapters'
                )
            ),
            to_attr='sections')
    ))


def get_tree(module):
    """
    Return a list of modules with the entire content on it
    :return:
    """
    sections = list(_Section.objects.filter(module=module).order_by('order').prefetch_related(
        Prefetch(
            'chapter_set',
            queryset=_Chapter.objects.order_by(
                'order').prefetch_related(
                Prefetch(
                    'topic_set',
                    queryset=_Topic.objects.order_by(
                        'order'),
                    to_attr='topics')),
            to_attr='chapters')))
    module.sections = sections
    return sections


def topics_user_interacted_queryset(user):
    return _Topic.objects.filter(
        topicinteraction__user=user
    ).select_related('chapter').select_related('chapter__section').select_related(
        'chapter__section__module'
    )
