from django.contrib import admin

from pythonpro.redirector.models import Redirect, RedirectLink


class RedirectLinkAdmin(admin.TabularInline):
    model = RedirectLink
    extra = 1
    readonly_fields = ['total_access', ]
    exclude = ['created', 'updated']


@admin.register(Redirect)
class RedirectorAdmin(admin.ModelAdmin):
    list_display = 'slug url'.split()
    inlines = (RedirectLinkAdmin, )
    exclude = ['created', 'updated']
