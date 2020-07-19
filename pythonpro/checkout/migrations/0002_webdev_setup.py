from django.db import migrations


def setup_payment_configs(apps, schema_editor):
    PagarmeFormConfig = apps.get_model('django_pagarme', 'PagarmeFormConfig')
    PagarmeItemConfig = apps.get_model('django_pagarme', 'PagarmeItemConfig')
    print()
    setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig)


def setup_payment_configs_function(PagarmeFormConfig, PagarmeItemConfig):
    """"""
    config = PagarmeFormConfig.objects.first()

    PagarmeItemConfig(
        name='Webdev Django',
        slug='webdev',
        price=99700,
        tangible=False,
        default_config=config,
    ).save()
    PagarmeItemConfig(
        name='Webdev Django 50% de Desconto',
        slug='webdev-oto',
        price=49700,
        tangible=False,
        default_config=config,
    ).save()


class Migration(migrations.Migration):
    dependencies = [
        ('checkout', '0001_payment_setup'),
    ]

    operations = [
        migrations.RunPython(setup_payment_configs, migrations.RunPython.noop)
    ]
