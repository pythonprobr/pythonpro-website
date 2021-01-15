# Generated by Django 3.0.4 on 2020-03-16 20:26

from django.db import migrations


def setup_payment_configs(apps, schema_editor):
    PagarmeFormConfig = apps.get_model('django_pagarme', 'PagarmeFormConfig')
    PagarmeItemConfig = apps.get_model('django_pagarme', 'PagarmeItemConfig')
    print()
    setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig)


def setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig):
    """"""
    config_card = PagarmeFormConfig.objects.all()[1]
    bootcamp_d1_boleto = 'bootcamp-d1-boleto'
    bootcamp_d1_config = PagarmeItemConfig(
        name='Bootcamp DevPro - R$1000 Off',
        slug=bootcamp_d1_boleto,
        price=199700,
        tangible=False,
        default_config=config_card
    )
    bootcamp_d1_config.save()

    webdev_downsell_slug = 'webdev-downsell'
    webdev_downsell_config = PagarmeItemConfig(
        name='Treinamento Webdev Django',
        slug=webdev_downsell_slug,
        price=49700,
        tangible=False,
        default_config=config_card
    )
    webdev_downsell_config.save()

    webdev_downsell_boleto_slug = 'webdev-downsell-boleto'
    webdev_downsell_boleto_config = PagarmeItemConfig(
        name='Treinamento Webdev Django',
        slug=webdev_downsell_boleto_slug,
        price=49700,
        tangible=False,
        default_config=config_card
    )
    webdev_downsell_boleto_config.save()

    aps_slug = 'aps'
    aps_config = PagarmeItemConfig(
        name='Acompanhamento de Processos Seletivos',
        slug=aps_slug,
        price=50000,
        tangible=False,
        default_config=config_card
    )
    aps_config.save()


class Migration(migrations.Migration):
    dependencies = [
        ('checkout', '0007_webserie_and_webinar_boleto'),
    ]

    operations = [
        migrations.RunPython(setup_payment_configs, migrations.RunPython.noop)
    ]
