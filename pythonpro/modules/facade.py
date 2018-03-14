from django.db.models import Prefetch

from pythonpro.modules.models import Section as _Section, Module as _Module


def get_all_modules():
    """
    Search all modules on database sorted by order
    :return: tuple of Module
    """
    return tuple(_Module.objects.order_by('order'))


def get_module_sections(slug):
    """
    Search for a module with respective sections
    :param slug: module slugs
    :return: Module with respective section on attribute sections
    """

    return _Module.objects.filter(slug=slug).prefetch_related(
        Prefetch(
            'section_set',
            queryset=_Section.objects.order_by('order'),
            to_attr='sections')
    ).get()
