from django.contrib import admin

from pythonpro.promos.models import Video


class VideoAdmin(admin.ModelAdmin):
    list_display = ['title']
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Video, VideoAdmin)
