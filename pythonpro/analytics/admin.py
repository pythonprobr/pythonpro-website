from django.contrib import admin

from pythonpro.analytics.models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    def get_session_user(self, obj, *args, **kwargs):
        return obj.session.user

    def get_path(self, obj, *args, **kwargs):
        return obj.meta.get('PATH_INFO')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    get_session_user.short_description = 'Usuário'
    get_path.short_description = 'Destino'
    list_display = ['id', 'get_path', 'session', 'get_session_user', 'created']
    search_fields = ['session__user__email']
