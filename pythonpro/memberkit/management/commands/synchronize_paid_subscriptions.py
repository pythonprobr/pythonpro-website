from django.core.management.base import BaseCommand
from django_pagarme import facade as pagarme_facade
from django_pagarme.models import PagarmePayment

from pythonpro.memberkit import facade


class Command(BaseCommand):
    help = 'Cria Assinatura para pagamentos que já tiveram status pago'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for payment in PagarmePayment.objects.filter(notifications__status=pagarme_facade.PAID, subscription=None):
            self.stdout.write(self.style.SUCCESS(f'Processando pagamento {payment}'))
            facade.create_new_subscription(payment, 'Criado através de comando de sincronização')
