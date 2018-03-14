from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from pythonpro.modules.models import Section


class SectionAdmin(OrderedModelAdmin):
    list_display = 'title slug _module_slug order move_up_down_links'.split()


admin.site.register(Section, SectionAdmin)
