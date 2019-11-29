from django.core.management import BaseCommand

from pythonpro.domain import user_facade


class Command(BaseCommand):
    help = 'Mark users for pytools 4 day promotion'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        promotion_users = user_facade.run_pytools_promotion_campaign()
        self.stdout.write(self.style.SUCCESS(f'Successfully marked {promotion_users} users for promotions'))
