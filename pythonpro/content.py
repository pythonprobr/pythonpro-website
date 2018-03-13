from abc import ABC, abstractmethod


class ContentMixing(ABC):
    """Mixing for defining content that can produce a breacrumb interface"""

    @abstractmethod
    def parent(self):
        """Must return the parent of current content, which must be also implement ContentMixing or None"""

    @abstractmethod
    def breadcrumb(self):
        """Must return a i"""

    @abstractmethod
    def get_absolute_url(self):
        """Must return the absolute url for this content"""


def gen_breadcrum(content):
    """Function that generates breadcrumb for contents that respect ContentMixing protocol"""
    parent = content.parent()
    if parent is not None:
        yield from parent.breadcrumb()
    yield content.title, content.get_absolute_url()


class ContentWithTitleMixin(ContentMixing):
    """
    Mising implementing breadcrumb method for models which has a title
    """

    def breadcrumb(self):
        return gen_breadcrum(self)
