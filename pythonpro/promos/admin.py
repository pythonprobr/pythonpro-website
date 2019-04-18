from django.contrib import admin
from django.utils.safestring import mark_safe

from pythonpro.promos.models import Video


class VideoAdmin(admin.ModelAdmin):
    list_display = 'title page_link'.split()
    prepopulated_fields = {'slug': ('title',)}

    def page_link(self, content):
        return mark_safe(f'<a href="{content.get_absolute_url()}">See on Page</a>')


admin.site.register(Video, VideoAdmin)
