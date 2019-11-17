from django.contrib import admin

from pythonpro.analytics.models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'created']
