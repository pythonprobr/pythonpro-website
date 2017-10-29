from django.contrib import admin

from pythonpro.leads.models import Lead


class LeadAdmin(admin.ModelAdmin):
    list_display = 'name email creation'.split()
    date_hierarchy = 'creation'


admin.site.register(Lead, LeadAdmin)
