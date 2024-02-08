from django.core.management import BaseCommand

from pythonpro.discord import facade


class Command(BaseCommand):
    help = 'Sincronizar usuários do Discord com Painel da DevPro'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        facade.clean_discord_users()
