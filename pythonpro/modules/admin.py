from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from pythonpro.modules.models import Section, Module


class SectionAdmin(OrderedModelAdmin):
    list_display = 'title slug module order move_up_down_links'.split()


class ModuleAdmin(OrderedModelAdmin):
    list_display = 'title slug order move_up_down_links'.split()


admin.site.register(Section, SectionAdmin)
admin.site.register(Module, ModuleAdmin)
