from importlib import import_module

import pytest
from django.contrib.auth.models import Group
from model_bakery import baker

# Workaround since module beginning with number can't be imported in regular way
migration_module = import_module('pythonpro.core.migrations.0011_normalizing_lead_email')


def test_no_msg_for_already_normalized_emails(django_user_model):
    baker.make(django_user_model, email='lower@python.pro.br')
    msg = next(migration_module.normalize_all_user_leads_emails(django_user_model), None)
    assert msg is None


@pytest.mark.parametrize('role', 'client member'.split())
def test_conflicting_email_msg_for_non_leads(django_user_model, role):
    lower_email = 'normalized@python.pro.br'
    upper_email = 'NORMALIZED@python.pro.br'
    group = baker.make(Group, name=role)
    upper_email_user = baker.make(django_user_model, email=upper_email, groups=[group])
    baker.make(django_user_model, email=lower_email)
    msg = next(migration_module.normalize_all_user_leads_emails(django_user_model))
    upper_email_user = django_user_model.objects.get(id=upper_email_user.id)
    assert msg == f'User groups {role} user {upper_email_user.id}, {upper_email_user.email}'


def test_conflicting_email_excluded(django_user_model):
    lower_email = 'normalized@python.pro.br'
    group = baker.make(Group, name='lead')
    baker.make(django_user_model, email='NORMALIZED@python.pro.br', groups=[group])
    baker.make(django_user_model, email='NORMALIZEd@python.pro.br', groups=[group])
    baker.make(django_user_model, email=lower_email)
    msg = next(migration_module.normalize_all_user_leads_emails(django_user_model), None)
    assert msg is None
    first_user, second_user, *_ = list(django_user_model.objects.order_by('id').all())
    assert first_user.email == f'excluded1.{lower_email}'
    assert second_user.email == f'excluded2.{lower_email}'
