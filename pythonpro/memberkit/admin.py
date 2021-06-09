from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
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


class PaymentListFilter(admin.SimpleListFilter):
    title = 'Por Pagamento'
    parameter_name = 'has_payment'

    def lookups(self, request, model_admin):
        return [('yes', 'Com Pagamento'), ('no', 'Sem Pagamento')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(payment_id__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(payment_id__isnull=True)
        return queryset


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    fields = ['payment', 'subscriber', 'subscription_types', 'observation']
    list_display = ['subscriber', 'pagarme_url_field', 'responsible', 'status', 'created_at', 'updated_at']
    autocomplete_fields = ['subscriber']
    search_fields = ['subscriber__email', 'payment__transaction_id']
    list_filter = ['status', PaymentListFilter, 'subscription_types']
    ordering = ['-updated_at']

    def get_queryset(self, request):
        return Subscription.objects.select_related('payment').select_related('subscriber').select_related('responsible')

    def pagarme_url_field(self, obj):
        if obj.payment is None:
            return '----'
        link = (
            f'<a href="https://beta.dashboard.pagar.me/#/transactions/'
            f'{obj.payment.transaction_id}">{obj.payment.transaction_id}</a>'
        )
        return format_html(link)

    pagarme_url_field.allow_tags = True
    pagarme_url_field.short_description = 'Link Pagarme'

    def has_delete_permission(self, request, obj=None):
        return False
