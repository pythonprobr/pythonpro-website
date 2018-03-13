from django.db import models
from django.urls import reverse
from ordered_model.models import OrderedModel

from pythonpro.content import gen_breadcrum
from pythonpro.modules import ALL_MODULES


class Section(OrderedModel):
    title = models.CharField(max_length=50)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    _module_slug = models.SlugField(choices=((m.slug, m.title) for m in ALL_MODULES.values()))
    order_with_respect_to = '_module_slug'

    class Meta:
        ordering = ['_module_slug', 'order']

    def get_absolute_url(self):
        return reverse('sections:detail', kwargs={'slug': self.slug})

    def parent(self):
        return ALL_MODULES[self._module_slug]

    def breadcrumb(self):
        return gen_breadcrum(self)
