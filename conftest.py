import pytest
from faker import Faker
from model_mommy import mommy
from rolepermissions.roles import assign_role

from pythonpro.cohorts.models import Cohort


@pytest.fixture
def fake():
    return Faker('pt_BR')


@pytest.fixture
def client_with_user(client, django_user_model, logged_user):
    client.force_login(logged_user)
    return client


@pytest.fixture
def logged_user(django_user_model):
    logged_user = mommy.make(django_user_model)
    logged_user.email = logged_user.email.lower()
    logged_user.save()
    return logged_user


@pytest.fixture
def cohort(db):
    return mommy.make(Cohort)


@pytest.fixture
def client_with_lead(client, django_user_model, logged_user):
    assign_role(logged_user, 'lead')
    client.force_login(logged_user)
    return client


@pytest.fixture
def client_with_webdev(client, django_user_model, logged_user):
    assign_role(logged_user, 'webdev')
    client.force_login(logged_user)
    return client


@pytest.fixture
def client_with_member(client, django_user_model, logged_user):
    assign_role(logged_user, 'member')
    client.force_login(logged_user)
    return client


@pytest.fixture
def client_with_client(client, django_user_model, logged_user):
    assign_role(logged_user, 'client')
    client.force_login(logged_user)
    return client


@pytest.fixture(autouse=True)
def use_db_always(db):
    pass


@pytest.fixture(autouse=True)
def turn_active_campaign_on(settings):
    """
    This way test don't depend on local .env configuration
    """
    settings.ACTIVE_CAMPAIGN_TURNED_ON = True


@pytest.fixture(autouse=True)
def turn_ssl_rediret_off_for_tests(settings):
    """
    There is no need to place secure=True in all client requests
    """
    settings.SECURE_SSL_REDIRECT = False


pytest_plugins = ['pythonpro.modules.tests.test_topics_view']
