from django.contrib import admin

from pythonpro.sections.models import Section


class SectionAdmin(admin.ModelAdmin):
    list_display = 'title slug _module_slug'.split()


admin.site.register(Section, SectionAdmin)
