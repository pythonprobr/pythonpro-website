from django.contrib import admin

from pythonpro.cohorts.models import Cohort


@admin.register(Cohort)
class ModuleAdmin(admin.ModelAdmin):
    list_display = 'title start end'.split()
    ordering = ('-start',)
