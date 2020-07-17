from importlib import import_module

import pytest
from django_pagarme import facade
from django_pagarme.models import PagarmeFormConfig, PagarmeItemConfig

# Workaround since module beginning with number can't be imported in regular way
migration_module = import_module('pythonpro.checkout.migrations.0001_payment_setup')
webdev_migration_module = import_module('pythonpro.checkout.migrations.0002_webdev_setup')


@pytest.fixture(autouse=True)
def execute_migration(db, pytestconfig):
    if pytestconfig.known_args_namespace.nomigrations:
        migration_module.setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig)
        webdev_migration_module.setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig)


def test_config_creation():
    assert PagarmeFormConfig.objects.count() == 1


def test_config_properties():
    config = PagarmeFormConfig.objects.first()
    assert (
               config.name,
               config.max_installments,
               config.default_installment,
               config.free_installment,
               config.interest_rate,
               config.payments_methods,
           ) == (
               'Boleto ou Cartão 12 vezes juros 1.66%',
               12,
               1,
               1,
               1.66,
               'credit_card,boleto'
           )


def test_item_config_pytools():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('pytools')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Curso Pytools',
               'pytools',
               39700,
               False,
               config
           )


def test_item_config_pytools_oto():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('pytools-oto')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Curso Pytools 75 Off',
               'pytools-oto',
               9700,
               False,
               config
           )


def test_item_config_pytools_done():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('pytools-done')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Curso Pytools 50 Off',
               'pytools-done',
               19850,
               False,
               config
           )


def test_item_membership():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('membership')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Inscricão Turma Python Pro',
               'membership',
               199700,
               False,
               config
           )


def test_item_membership_for_client():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('membership-client')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Inscricão Turma Python Pro 100 R Off',
               'membership-client',
               189700,
               False,
               config
           )


def test_item_membership_for_client_first_day():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('membership-client-first-day')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Inscricão Turma Python Pro 500 R Off',
               'membership-client-first-day',
               149700,
               False,
               config
           )


def test_item_membership_first_day():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('membership-first-day')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Inscricão Turma Python Pro 400 R Off',
               'membership-first-day',
               159700,
               False,
               config
           )


def test_item_webdev_oto():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('webdev-oto')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Webdev Django 50% de Desconto',
               'webdev-oto',
               49700,
               False,
               config
           )


def test_item_webdev():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('webdev')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Webdev Django',
               'webdev',
               99700,
               False,
               config
           )


def test_item_data_science():
    config = PagarmeFormConfig.objects.first()
    item_config = facade.find_payment_item_config('data-science')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Ciência de Dados',
               'data-science',
               49700,
               False,
               config
           )
