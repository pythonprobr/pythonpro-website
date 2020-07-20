from django.db import migrations


def setup_payment_configs(apps, schema_editor):
    PagarmeFormConfig = apps.get_model('django_pagarme', 'PagarmeFormConfig')
    PagarmeItemConfig = apps.get_model('django_pagarme', 'PagarmeItemConfig')
    print()
    setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig)


def setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig):
    """"""
    config = PagarmeFormConfig(
        name='Boleto ou Cartão 12 vezes juros 1.66%',
        max_installments=12,
        default_installment=1,
        free_installment=1,
        interest_rate=1.66,
        payments_methods='credit_card,boleto',
    )
    config.save()

    PagarmeItemConfig(
        name='Curso Pytools',
        slug='pytools',
        price=39700,
        tangible=False,
        default_config=config,
    ).save()

    PagarmeItemConfig(
        name='Curso Pytools 75 Off',
        slug='pytools-oto',
        price=9700,
        tangible=False,
        default_config=config,
    ).save()

    PagarmeItemConfig(
        name='Curso Pytools 50 Off',
        slug='pytools-done',
        price=19850,
        tangible=False,
        default_config=config,
    ).save()

    PagarmeItemConfig(
        name='Inscricão Turma Python Pro',
        slug='membership',
        price=199700,
        tangible=False,
        default_config=config,
    ).save()
    PagarmeItemConfig(
        name='Inscricão Turma Python Pro 100 R Off',
        slug='membership-client',
        price=189700,
        tangible=False,
        default_config=config,
    ).save()
    PagarmeItemConfig(
        name='Inscricão Turma Python Pro 500 R Off',
        slug='membership-client-first-day',
        price=149700,
        tangible=False,
        default_config=config,
    ).save()
    PagarmeItemConfig(
        name='Inscricão Turma Python Pro 400 R Off',
        slug='membership-first-day',
        price=159700,
        tangible=False,
        default_config=config,
    ).save()


class Migration(migrations.Migration):
    dependencies = [
        ('django_pagarme', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(setup_payment_configs, migrations.RunPython.noop)
    ]
