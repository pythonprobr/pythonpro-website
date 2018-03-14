from django.db import models
from django.urls import reverse
from ordered_model.models import OrderedModel

ALL = {}


class Content(OrderedModel):
    """Mixing for defining content that can produce a breacrumb interface"""
    title = models.CharField(max_length=50)
    description = models.TextField()
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True
        ordering = ('order',)

    def parent(self):
        """Must return the parent of current content, which must be also implement Content or None"""
        raise NotImplementedError()

    def breadcrumb(self):
        """Must return an iterable with where which item is a tuple of (title, url) to content """
        return gen_breadcrum(self)

    def get_absolute_url(self):
        """Must return the absolute url for this content"""
        return reverse('modules:detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class ContentWithTitleMixin(Content):
    """
    Mising implementing breadcrumb method for models which has a title
    """

    class Meta:
        abstract = True

    def breadcrumb(self):
        return gen_breadcrum(self)


def gen_breadcrum(content):
    """Function that generates breadcrumb for contents that respect Content protocol"""
    parent = content.parent()
    if parent is not None:
        yield from parent.breadcrumb()
    yield content.title, content.get_absolute_url()


class Module(Content):
    objective = models.TextField()
    target = models.TextField()

    def parent(self):
        return None


class Section(Content):
    _module_slug = models.SlugField(choices=((m.slug, m.title) for m in ALL.values()))
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    order_with_respect_to = '_module_slug'

    class Meta:
        ordering = ['_module_slug', 'order']

    def get_absolute_url(self):
        return reverse('sections:detail', kwargs={'slug': self.slug})

    def parent(self):
        return self.module
