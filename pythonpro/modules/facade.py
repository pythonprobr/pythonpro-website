from django.db.models import Prefetch

from pythonpro.modules.models import (Section as _Section, Module as _Module, Chapter as _Chapter, Topic as _Topic)


def get_all_modules():
    """
    Search all modules on database sorted by order
    :return: tuple of Module
    """
    return tuple(_Module.objects.order_by('order'))


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
