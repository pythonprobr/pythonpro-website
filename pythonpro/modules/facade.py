from django.urls import reverse as _reverse

from pythonpro.modules.models import Section as _Section


def get_module_sections(module):
    """
    Search for all module's sections. Only Section's title and slug is returned
    :param module:
    :return:
    """

    def set_absolut_url(dct):
        dct['get_absolute_url'] = _reverse('sections:detail', kwargs={'slug': dct['slug']})
        return dct

    mapped = map(
        set_absolut_url,
        _Section.objects.values('title', 'slug').filter(_module_slug=module.slug).order_by('order')
    )

    return tuple(mapped)
