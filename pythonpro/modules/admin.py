from django.contrib import admin
from django.utils.safestring import mark_safe
from ordered_model.admin import OrderedModelAdmin

from pythonpro.modules.models import Section, Module, Chapter, Topic


class BaseAdmin(OrderedModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    view_on_site = True

    def page_link(self, content):
        return mark_safe(f'<a href="{content.get_absolute_url()}">See on Page</a>')

    page_link.short_description = 'page'


@admin.register(Module)
class ModuleAdmin(BaseAdmin):
    list_display = 'title slug order move_up_down_links page_link'.split()


@admin.register(Section)
class SectionAdmin(BaseAdmin):
    list_display = 'title slug module order move_up_down_links page_link'.split()


@admin.register(Chapter)
class ChapterAdmin(BaseAdmin):
    list_display = 'title slug section order move_up_down_links page_link'.split()


@admin.register(Topic)
class TopicAdmin(BaseAdmin):
    list_display = 'title slug chapter order move_up_down_links page_link'.split()
    list_filter = ('chapter',)
