from importlib import import_module

import pytest
from django_pagarme import facade
from django_pagarme.models import PagarmeFormConfig, PagarmeItemConfig

# Workaround since module beginning with number can't be imported in regular way

migration_module = import_module('pythonpro.checkout.migrations.0001_payment_setup')
webdev_migration_module = import_module('pythonpro.checkout.migrations.0002_webdev_setup')
data_science_migration_module = import_module('pythonpro.checkout.migrations.0003_data_science_setup')

ALL_ACTIVE_PRODUCTS = [
    'membership',
    'membership-client',
    'membership-client-first-day',
    'membership-first-day',
    'webdev',
    'webdev-oto',
    'data-science',
]
ALL_INACTIVE_PRODUCTS = [
    'pytools',
    'pytools-oto',
    'pytools-done',
]
ALL_PRODUCTS = ALL_ACTIVE_PRODUCTS + ALL_INACTIVE_PRODUCTS


@pytest.fixture(autouse=True)
def execute_migration(db, pytestconfig):
    if pytestconfig.known_args_namespace.nomigrations:
        migration_module.setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig)
        webdev_migration_module.setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig)
        data_science_migration_module.setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig)


@pytest.fixture(autouse=True)
def disable_email_marketing(settings):
    settings.ACTIVE_CAMPAIGN_TURNED_ON = False


@pytest.fixture(autouse=True)
def disable_forum_integration(settings):
    settings.DISCOURSE_BASE_URL = ''
    settings.DISCOURSE_SSO_SECRET = ''
    settings.DISCOURSE_API_KEY = ''
    settings.DISCOURSE_API_USER = ''


@pytest.fixture(params=ALL_ACTIVE_PRODUCTS)
def active_product_item(execute_migration, cohort, request):
    slug = request.param
    return facade.find_payment_item_config(slug)
