from django.core.management.base import BaseCommand

from pythonpro.memberkit import facade


class Command(BaseCommand):
    help = 'Busca todas assinaturas ativas e inativa as que estão expiradas'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        facade.inactivate_expired_subscriptions()
