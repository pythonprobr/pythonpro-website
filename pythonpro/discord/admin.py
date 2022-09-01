from django.contrib import admin

from pythonpro.discord.models import DiscordUser


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    fields = ['user', 'discord_id', 'discord_email', 'created_at']
    list_display = fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
