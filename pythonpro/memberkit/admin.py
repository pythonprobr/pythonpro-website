from time import strftime

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django_pagarme.admin import PagarmeItemConfigAdmin
from django_pagarme.models import PagarmeItemConfig

# Register your models here.
from pythonpro.domain import subscription_domain
from pythonpro.memberkit import facade
from pythonpro.memberkit.models import SubscriptionType, PaymentItemConfigToSubscriptionType, Subscription


class PaymentItemConfigInline(admin.TabularInline):
    extra = 1
    model = PaymentItemConfigToSubscriptionType


@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    change_list_template = 'memberkit/subscriptiontype/synchronize_button.html'
    fields = [
        'id',
        'name',
        'has_discord_access',
        'email_marketing_tags',
        'discourse_groups',
        'include_on_cohort',
        'days_of_access'
    ]
    list_display = fields
    readonly_fields = ['id', 'name']
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
    fields = ['payment', 'subscriber', 'subscription_types', 'observation', 'days_of_access']
    list_display = [
        'id', 'subscriber', 'pagarme_url_field', 'memberkit_user_url_field', 'responsible', 'status',
        'created_at', 'updated_at', 'activated_at', 'expires_at'
    ]
    autocomplete_fields = ['subscriber']
    search_fields = ['subscriber__email', 'payment__transaction_id']
    list_filter = ['status', PaymentListFilter, 'subscription_types']
    ordering = ['-updated_at']
    readonly_fields = ['activated_at', 'memberkit_user_id']
    actions = ['activate', 'inactivate']

    def get_queryset(self, request):
        return Subscription.objects.select_related('payment').select_related('subscriber').select_related('responsible')

    def pagarme_url_field(self, obj):
        if obj.payment is None:
            link = (
                f'<a href="https://beta.dashboard.pagar.me/#/transactions?search='
                f'{obj.subscriber.email}" target="_blank">Buscar</a>'
            )
        else:
            link = (
                f'<a href="https://beta.dashboard.pagar.me/#/transactions/'
                f'{obj.payment.transaction_id}" target="_blank">{obj.payment.transaction_id}</a>'
            )
        return format_html(link)

    pagarme_url_field.allow_tags = True
    pagarme_url_field.short_description = 'Pagarme'

    def memberkit_user_url_field(self, obj):
        if obj.memberkit_user_id is None:
            return '----'
        link = (
            f'<a href="https://plataforma.dev.pro.br/members/{obj.memberkit_user_id}/edit">'
            f'{obj.subscriber.first_name}</a>'
        )
        return format_html(link)

    memberkit_user_url_field.allow_tags = True
    memberkit_user_url_field.short_description = 'Memberkit'

    def activate(self, request, queryset):
        responsible = request.user
        for subscription in queryset:
            subscription_domain.activate_subscription_on_all_services(
                subscription,
                responsible,
                f'Ativada via admin por Usuário com id {responsible.id} e email {responsible.email}'
            )

    activate.short_descriptions = 'Ativar'

    def inactivate(self, request, queryset):
        responsible = request.user
        strftime('d%/%m/%Y H%:%M:%S')
        for subscription in queryset:
            subscription_domain.inactivate_subscription_on_all_services(
                subscription,
                responsible,
                f'Desativada em via admin por Usuário com id {responsible.id} e email {responsible.email}'
            )

    inactivate.short_descriptions = 'Desativar'

    def has_delete_permission(self, request, obj=None):
        return False
