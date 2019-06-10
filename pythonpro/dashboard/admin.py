from django.contrib import admin

from pythonpro.dashboard.models import TopicInteraction


@admin.register(TopicInteraction)
class TopicInteractionAdmin(admin.ModelAdmin):
    list_display = 'creation user topic topic_duration total_watched_time max_watched_time'.split()
    list_filter = ('topic', 'user')
    ordering = ('-creation',)
