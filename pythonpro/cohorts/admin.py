from django.contrib import admin
from django.utils.safestring import mark_safe

from pythonpro.cohorts.models import Cohort, LiveClass, Webinar


class ClassInline(admin.TabularInline):
    extra = 1
    model = LiveClass
    ordering = ('start',)


class StudentInline(admin.TabularInline):
    readonly_fields = ('added',)
    extra = 1
    autocomplete_fields = ['user']
    model = Cohort.students.through
    ordering = ('added',)


class WebinarInline(admin.StackedInline):
    extra = 1
    model = Webinar
    ordering = ('start',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    inlines = [ClassInline, WebinarInline, StudentInline]
    prepopulated_fields = {'slug': ('title',)}
    list_display = 'title start end page_link'.split()
    ordering = ('-start',)

    def page_link(self, cohort):
        return mark_safe(f'<a href="{cohort.get_absolute_url()}">See on Page</a>')

    page_link.short_description = 'page'
