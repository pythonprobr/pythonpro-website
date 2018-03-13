from django.db import models

from pythonpro.modules import ALL_MODULES


class Section(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    _module_slug = models.SlugField(choices=((m.slug, m.title) for m in ALL_MODULES.values()))

    class Meta:
        ordering = ['_module_slug', 'title']
