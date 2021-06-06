from django.core.management.base import BaseCommand
from django.db.models import OuterRef, Subquery
from django_pagarme import facade as pagarme_facade
from django_pagarme.models import PagarmePayment, PagarmeNotification

from pythonpro.memberkit.models import Subscription


class Command(BaseCommand):
    help = 'Ativa assinatura inativas que possuem última notificação de pagamento como paga'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        last_notification = PagarmeNotification.objects.filter(payment=OuterRef('pk')).order_by('-creation')
        qs = PagarmePayment.objects.filter(
            notifications__status=pagarme_facade.PAID,
            subscription__isnull=False
        ).only(
            'subscription'
        ).select_related(
            'subscription'
        ).select_related(
            'subscription__subscriber'
        ).filter(
            subscription__status=Subscription.Status.INACTIVE
        ).annotate(
            payment_status=Subquery(last_notification.values('status')[:1])
        ).filter(payment_status=pagarme_facade.PAID)
        for payment in qs:
            subscription = payment.subscription
            self.stdout.write(self.style.SUCCESS(f'Processando {subscription}'))
            subscription.observation += '\n\nAtivada via comando automático do servidor.'
            subscription.status = Subscription.Status.ACTIVE
            subscription.save()
