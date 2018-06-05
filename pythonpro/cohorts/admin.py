from django.contrib import admin
from django.utils.safestring import mark_safe

from pythonpro.cohorts.models import Cohort, LiveClass, Webinar


class ClassInline(admin.TabularInline):
    extra = 1
    model = LiveClass
    ordering = ('start',)


class WebinarInline(admin.StackedInline):
    extra = 1
    model = Webinar
    ordering = ('start',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Cohort)
class ModuleAdmin(admin.ModelAdmin):
    inlines = [ClassInline, WebinarInline]
    prepopulated_fields = {'slug': ('title',)}
    list_display = 'title start end page_link'.split()
    ordering = ('-start',)

    def page_link(self, cohort):
        return mark_safe(f'<a href="{cohort.get_absolute_url()}">See on Page</a>')

    page_link.short_description = 'page'
