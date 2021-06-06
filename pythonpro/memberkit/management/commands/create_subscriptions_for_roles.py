from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from pythonpro.memberkit.models import Subscription


class Command(BaseCommand):
    help = 'Cria Assinatura para usuários sem pagamentos'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        role_to_subscription_type_dct = {
            'data_scientist': 4456,
            'webdev': 4426,
            'member': 4424,
            'bootcamper': 4423,
            'pythonista': 4423,
            'client': 4420,
        }
        for role, subscription_type_id in role_to_subscription_type_dct.items():
            users_with_role = get_user_model().objects.filter(
                groups__name=role
            ).exclude(subscriptions__subscription_types__id=subscription_type_id).only('id')
            for user in users_with_role:
                self.stdout.write(self.style.SUCCESS(f'Processando usuário {user} com papel {role}'))
                subscription = Subscription.objects.create(
                    subscriber_id=user.id,
                    status=Subscription.Status.INACTIVE,
                    observation='Assinatura sem pagamento criada automaticamente por comando no servidor'
                )
                subscription.subscription_types.set([subscription_type_id])
                self.stdout.write(self.style.SUCCESS(f'Criada {subscription}'))
