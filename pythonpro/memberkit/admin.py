from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django_pagarme.admin import PagarmeItemConfigAdmin
from django_pagarme.models import PagarmeItemConfig

# Register your models here.
from pythonpro.memberkit import facade
from pythonpro.memberkit.models import SubscriptionType, PaymentItemConfigToSubscriptionType, Subscription


class PaymentItemConfigInline(admin.TabularInline):
    extra = 1
    model = PaymentItemConfigToSubscriptionType


@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    change_list_template = "memberkit/subscriptiontype/synchronize_button.html"
    fields = ['id', 'name']
    list_display = fields
    readonly_fields = fields
    inlines = [PaymentItemConfigInline]

    def get_urls(self):
        urls = super().get_urls()
        urls.append(path('sincronizar', self.synchronize))
        return urls

    def synchronize(self, request):
        facade.synchronize_subscription_types()
        self.message_user(request, 'Assinaturas Atualizadas')
        return redirect('.')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(PagarmeItemConfig)


@admin.register(PagarmeItemConfig)
class NewPagarmeItemConfigAdmin(PagarmeItemConfigAdmin):
    inlines = [PaymentItemConfigInline]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    fields = ['subscriber', 'subscription_types', 'observation']
    list_display = ['subscriber', 'responsible', 'status', 'created_at', 'updated_at']
    autocomplete_fields = ['subscriber']
    search_fields = ['subscriber__email']
    list_filter = ['status', 'subscription_types']

    def has_delete_permission(self, request, obj=None):
        return False
