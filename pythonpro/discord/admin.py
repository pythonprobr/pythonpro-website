from django.contrib import admin

from pythonpro.discord.models import DiscordUser, DiscordLead


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    fields = ['user', 'discord_id', 'discord_email', 'created_at']
    list_display = fields
    search_fields = ['discord_email', 'user__email']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DiscordLead)
class DiscordLeadAdmin(admin.ModelAdmin):
    fields = ["discord_id", "status", "created_at", "updated_at"]
    list_display = fields
    list_filter = ['status']
    ordering = ['-updated_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
