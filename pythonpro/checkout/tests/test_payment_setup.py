import pytest
from django_pagarme import facade
from django_pagarme.models import PagarmeFormConfig, PagarmeItemConfig


def test_config_creation():
    assert PagarmeFormConfig.objects.count() == 3


@pytest.fixture
def first_pagarme_form_config():
    return PagarmeFormConfig.objects.order_by('id').first()


def test_first_config_properties(first_pagarme_form_config):
    assert (
               first_pagarme_form_config.name,
               first_pagarme_form_config.max_installments,
               first_pagarme_form_config.default_installment,
               first_pagarme_form_config.free_installment,
               first_pagarme_form_config.interest_rate,
               first_pagarme_form_config.payments_methods,
           ) == (
               'Boleto ou Cartão 12 vezes juros 1.66%',
               12,
               1,
               1,
               1.66,
               'credit_card,boleto'
           )


def test_item_config_pytools(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


def test_item_config_pytools_oto(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


def test_item_config_pytools_done(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


def test_webinar(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('treinamento-devpro-webinar')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Treinamento DevPro com 30% de Desconto',
               'treinamento-devpro-webinar',
               99700,
               False,
               first_pagarme_form_config
           )


def test_webinar_boleto(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('treinamento-devpro-webinar-boleto')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Treinamento DevPro com 30% de Desconto',
               'treinamento-devpro-webinar-boleto',
               99700,
               False,
               first_pagarme_form_config
           )


def test_webserie(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('treinamento-devpro-webserie')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Treinamento DevPro com 30% de Desconto',
               'treinamento-devpro-webserie',
               99700,
               False,
               first_pagarme_form_config
           )


def test_webserie_boleto(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('treinamento-devpro-webserie-boleto')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Treinamento DevPro com 30% de Desconto',
               'treinamento-devpro-webserie-boleto',
               99700,
               False,
               first_pagarme_form_config
           )


def test_masterclass_oto(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('treinamento-devpro-masterclass-oto')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Treinamento DevPro com 30% de Desconto',
               'treinamento-devpro-masterclass-oto',
               99700,
               False,
               first_pagarme_form_config
           )


def test_masterclass_oto_boleto(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('treinamento-devpro-masterclass-oto-boleto')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Treinamento DevPro com 30% de Desconto',
               'treinamento-devpro-masterclass-oto-boleto',
               99700,
               False,
               first_pagarme_form_config
           )


def test_item_membership(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


def test_item_membership_for_client(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


def test_item_membership_for_client_first_day(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


def test_item_membership_first_day(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


def test_item_webdev_oto(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


def test_item_webdev(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


def test_item_data_science(first_pagarme_form_config):
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
               first_pagarme_form_config
           )


@pytest.fixture
def second_pagarme_form_config():
    return PagarmeFormConfig.objects.order_by('id').all()[1]


def test_second_config_properties(second_pagarme_form_config):
    assert (
               second_pagarme_form_config.name,
               second_pagarme_form_config.max_installments,
               second_pagarme_form_config.default_installment,
               second_pagarme_form_config.free_installment,
               second_pagarme_form_config.interest_rate,
               second_pagarme_form_config.payments_methods,
           ) == (
               'Cartão 12 vezes juros 1.66%',
               12,
               1,
               1,
               1.66,
               'credit_card'
           )


def test_item_bootcamp(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('bootcamp')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Bootcamp Python Pro',
               'bootcamp',
               199700,
               False,
               first_pagarme_form_config
           )


def test_item_bootcamp_35_discount(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('bootcamp-35-discount')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Bootcamp Python Pro - 35% de Desconto',
               'bootcamp-35-discount',
               129700,
               False,
               first_pagarme_form_config
           )


def test_item_bootcamp_50_discount(second_pagarme_form_config):
    item_config = facade.find_payment_item_config('bootcamp-50-discount')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Bootcamp Python Pro - 50% de Desconto',
               'bootcamp-50-discount',
               99700,
               False,
               second_pagarme_form_config
           )


def test_item_bootcamp_webdev(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('bootcamp-webdev')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Bootcamp Python Pro - R$497 Off',
               'bootcamp-webdev',
               150000,
               False,
               first_pagarme_form_config
           )


def test_item_bootcamp_webdev_35_discount(first_pagarme_form_config):
    item_config = facade.find_payment_item_config('bootcamp-webdev-35-discount')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Bootcamp Python Pro - 35% de Desconto - R$497 Off',
               'bootcamp-webdev-35-discount',
               80000,
               False,
               first_pagarme_form_config
           )


def test_item_bootcamp_webdev_50_discount(second_pagarme_form_config):
    item_config = facade.find_payment_item_config('bootcamp-webdev-50-discount')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Bootcamp Python Pro - 50% de Desconto - R$497 Off',
               'bootcamp-webdev-50-discount',
               50000,
               False,
               second_pagarme_form_config
           )


def test_item_bootcamp_d1_boleto(second_pagarme_form_config):
    item_config = facade.find_payment_item_config('bootcamp-d1-boleto')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Bootcamp DevPro - R$1000 Off',
               'bootcamp-d1-boleto',
               199700,
               False,
               second_pagarme_form_config
           )


@pytest.fixture
def free_interest_form_config():
    return PagarmeFormConfig.objects.order_by('id').all()[2]


def test_free_interest_properties(free_interest_form_config):
    assert (
               free_interest_form_config.name,
               free_interest_form_config.max_installments,
               free_interest_form_config.default_installment,
               free_interest_form_config.free_installment,
               free_interest_form_config.interest_rate,
               free_interest_form_config.payments_methods,
           ) == (
               'Cartão ou Boleto 10 vezes sem juros',
               10,
               10,
               10,
               0,
               'credit_card,boleto'
           )


def test_item_python_avancado(free_interest_form_config):
    item_config = facade.find_payment_item_config('pacote-proximo-nivel-67-discount')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Pacote Python Avançado - 50% de Desconto',
               'pacote-proximo-nivel-67-discount',
               49700,
               False,
               free_interest_form_config
           )
    for payment_item in PagarmeItemConfig.objects.filter(slug__startswith='bootcamp').all():
        if not payment_item.slug.startswith('bootcamp-d'):
            assert payment_item.upsell_id == item_config.id


def test_item_webdev_downsell(second_pagarme_form_config):
    item_config = facade.find_payment_item_config('webdev-downsell')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Treinamento Webdev Django',
               'webdev-downsell',
               49700,
               False,
               second_pagarme_form_config
           )


def test_item_webdev_downsell_boleto(second_pagarme_form_config):
    item_config = facade.find_payment_item_config('webdev-downsell-boleto')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Treinamento Webdev Django',
               'webdev-downsell-boleto',
               49700,
               False,
               second_pagarme_form_config
           )


def test_item_aps(second_pagarme_form_config):
    item_config = facade.find_payment_item_config('aps')
    assert (
               item_config.name,
               item_config.slug,
               item_config.price,
               item_config.tangible,
               item_config.default_config,
           ) == (
               'Acompanhamento de Processos Seletivos',
               'aps',
               50000,
               False,
               second_pagarme_form_config
           )
