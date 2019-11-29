from django.contrib import admin

from pythonpro.dashboard.models import TopicInteraction


@admin.register(TopicInteraction)
class TopicInteractionAdmin(admin.ModelAdmin):
    list_display = 'creation user topic topic_duration total_watched_time max_watched_time'.split()
    ordering = ('-creation',)
    actions = None
    search_fields = ('user__email',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
