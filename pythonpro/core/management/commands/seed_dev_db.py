from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from django_pagarme.models import PagarmeFormConfig, PagarmeItemConfig, CREDIT_CARD


class Command(BaseCommand):
    help = "Seed dev deb with minimum data"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(
                self.style.WARNING(
                    'Not possible running seed with DEBUG being True. '
                    'This is a feature to avoid running this command on production.'
                )
            )
            return
        self.stdout.write(
            self.style.SUCCESS('Start db seeding...')
        )

        User = get_user_model()
        admin_email = 'admin@admin.com'
        if User.objects.filter(email=admin_email).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'There is already an User with email {admin_email}. So not admin created'
                )
            )
        else:
            self.stdout.write(
                'Creating admin user'
            )

            User.objects.create_superuser(first_name='Admin', email=admin_email, password='admin')

            self.stdout.write(
                self.style.SUCCESS('User created with email admin@admin.com and password "admin"')
            )

        pagarme_form_config = PagarmeFormConfig.objects.create(
            name='Cartão 12 vezes juros 1.66%',
            max_installments=12,
            default_installment=12,
            free_installment=1,
            interest_rate=1.66,
            payments_methods=CREDIT_CARD,
        )

        PagarmeItemConfig.objects.create(
            name='Comunidade DevPro',
            slug='comunidade-devpro',
            price=99700,
            tangible=False,
            default_config=pagarme_form_config,
        )
