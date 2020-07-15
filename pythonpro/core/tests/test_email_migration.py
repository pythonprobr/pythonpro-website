from importlib import import_module

from model_bakery import baker

# Workaround since module beginning with number can't be imported in regular way
migration_module = import_module('pythonpro.core.migrations.0010_normalizing_email')


def test_user_email_normalization_success(django_user_model):
    """Ensures email can be normalized"""

    upper_email = 'UPPER@python.pro.br'
    baker.make(django_user_model, email=upper_email)
    msg = next(migration_module.normalize_all_users_email(django_user_model), None)
    assert msg is None
    assert django_user_model.objects.first().email == upper_email.lower()


def test_no_msg_for_already_normalized_emails(django_user_model):
    baker.make(django_user_model, email='lower@python.pro.br')
    msg = next(migration_module.normalize_all_users_email(django_user_model), None)
    assert msg is None


def test_conflicting_email_msg(django_user_model):
    lower_email = 'normalized@python.pro.br'
    upper_email = 'NORMALIZED@python.pro.br'
    upper_email_user = baker.make(django_user_model, email=upper_email)
    baker.make(django_user_model, email=lower_email)
    msg = next(migration_module.normalize_all_users_email(django_user_model))
    upper_email_user = django_user_model.objects.get(id=upper_email_user.id)
    assert msg == f'Normalization error user {upper_email_user.id}, {upper_email_user.email}'
