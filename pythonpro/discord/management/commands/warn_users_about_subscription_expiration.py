from django.core.management import BaseCommand

from pythonpro.discord import facade


class Command(BaseCommand):
    help = 'Sincronizar usuários do Discord com Painel da DevPro'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        facade.warn_users_about_subscription_expiration()
