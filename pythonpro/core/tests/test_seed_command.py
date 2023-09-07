import pytest as pytest
from django.core import management


@pytest.fixture(autouse=True)
def set_debug_true(settings):
    """
    This way test don't depend on local .env configuration
    """
    settings.DEBUG = True


def test_seed_command_exists():
    management.call_command('seed_dev_db')


def test_admin_creation(django_user_model):
    management.call_command('seed_dev_db')
    User = django_user_model
    assert User.objects.count() == 1
    admin_user = User.objects.first()
    assert admin_user.first_name == 'Admin'
    assert admin_user.email == 'admin@admin.com'
    assert admin_user.is_superuser
    assert admin_user.check_password('admin')


def test_seed_not_execution_when_debug_is_false(django_user_model, settings):
    settings.DEBUG = False
    management.call_command('seed_dev_db')
    User = django_user_model
    assert not User.objects.exists()
