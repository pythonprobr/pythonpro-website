from django.contrib import admin
from django.utils.safestring import mark_safe

from pythonpro.cohorts.models import Cohort, LiveClass


class ClassInline(admin.TabularInline):
    extra = 1
    model = LiveClass


@admin.register(Cohort)
class ModuleAdmin(admin.ModelAdmin):
    inlines = [ClassInline]
    prepopulated_fields = {'slug': ('title',)}
    list_display = 'title start end page_link'.split()
    ordering = ('-start',)

    def page_link(self, cohort):
        return mark_safe(f'<a href="{cohort.get_absolute_url()}">See on Page</a>')

    page_link.short_description = 'page'
