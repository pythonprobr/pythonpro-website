from importlib import import_module

import pytest
from django_pagarme.models import PagarmeFormConfig, PagarmeItemConfig

# Workaround since module beginning with number can't be imported in regular way
migration_module = import_module('pythonpro.checkout.migrations.0001_payment_setup')


@pytest.fixture(autouse=True)
def execute_migration(db, pytestconfig):
    if pytestconfig.known_args_namespace.nomigrations:
        migration_module.setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig)
