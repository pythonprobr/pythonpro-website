from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from ordered_model.models import OrderedModel


class _NoneCache:
    pass


class Content(OrderedModel):
    """Mixing for defining content that can produce a breacrumb interface"""
    title = models.CharField(max_length=50)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    _next_content_cache = _NoneCache

    class Meta:
        abstract = True
        ordering = ('order',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parent(self):
        """Must return the parent of current content, which must be also implement Content or None"""
        raise NotImplementedError()

    def breadcrumb(self):
        """Must return an iterable with where which item is a tuple of (title, url) to content """
        return gen_breadcrum(self)

    def get_absolute_url(self):
        """Must return the absolute url for this content"""
        raise NotImplementedError()

    def __str__(self):
        return self.title

    def next_content(self):
        if self._next_content_cache is not _NoneCache:
            return self._next_content_cache
        current = self
        while current is not None:
            try:
                self._next_content_cache = current._next_content_query_set().get()
                break
            except ObjectDoesNotExist:
                current = current.parent()
        else:
            self._next_content_cache = None
        return self._next_content_cache

    def _next_content_query_set(self):
        """Must provide a query set for next content"""
        raise NotImplementedError()

    def module_slug(self):
        if self.parent() is None:
            return self.slug
        return self.parent().module_slug()


class ContentWithTitleMixin(Content):
    """
    Missing implementing breadcrumb method for models which has a title
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

    def get_absolute_url(self):
        """Must return the absolute url for this content"""
        return reverse('modules:detail', kwargs={'slug': self.slug})

    def _next_content_query_set(self):
        return Module.objects.filter(order=self.order + 1)


class Section(Content):
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    order_with_respect_to = 'module'

    class Meta:
        ordering = ['module', 'order']

    def get_absolute_url(self):
        return reverse('sections:detail', kwargs={'slug': self.slug})

    def parent(self):
        return self.module

    def _next_content_query_set(self):
        return Section.objects.filter(module=self.module, order=self.order + 1)


class Chapter(Content):
    section = models.ForeignKey('Section', on_delete=models.CASCADE)
    order_with_respect_to = 'section'

    class Meta:
        ordering = ['section', 'order']

    def get_absolute_url(self):
        return reverse('chapters:detail', kwargs={'slug': self.slug})

    def parent(self):
        return self.section

    def _next_content_query_set(self):
        return Chapter.objects.filter(section=self.section, order=self.order + 1)


class Topic(Content):
    chapter = models.ForeignKey('Chapter', on_delete=models.CASCADE)
    vimeo_id = models.CharField(max_length=11, db_index=False)
    discourse_topic_id = models.CharField(max_length=11, db_index=False)
    order_with_respect_to = 'chapter'

    class Meta:
        ordering = ['chapter', 'order']

    def get_absolute_url(self):
        return reverse('topics:detail', kwargs={'slug': self.slug})

    def parent(self):
        return self.chapter

    def _next_content_query_set(self):
        return Topic.objects.filter(chapter=self.chapter, order=self.order + 1)
