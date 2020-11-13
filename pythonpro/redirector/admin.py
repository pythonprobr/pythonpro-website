from django.contrib import admin
from django.utils.html import format_html

from pythonpro.redirector.models import Redirect, RedirectLink


class RedirectLinkAdmin(admin.TabularInline):
    model = RedirectLink
    extra = 1
    readonly_fields = ['total_access', ]
    exclude = ['created', 'updated']


@admin.register(Redirect)
class RedirectorAdmin(admin.ModelAdmin):
    list_display = ['slug', 'created', 'get_redirect_link']
    list_filter = ['use_javascript', 'created']
    inlines = (RedirectLinkAdmin, )
    exclude = ['created', 'updated']
    ordering = ['-updated', '-created', 'slug']

    def get_redirect_link(self, obj):
        return format_html(
            f"""<a href='{obj.get_absolute_url()}' class="button" target='_blank'>
                Link Gerado
            </a>""")

    get_redirect_link.short_description = 'Links'
