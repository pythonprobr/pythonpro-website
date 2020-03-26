from django.contrib import admin

from pythonpro.redirector.models import Redirect


@admin.register(Redirect)
class RedirectorAdmin(admin.ModelAdmin):
    list_display = 'slug url'.split()
