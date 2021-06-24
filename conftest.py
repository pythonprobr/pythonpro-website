import posthog
import pytest
from faker import Faker
from model_bakery import baker
from rolepermissions.roles import assign_role

from pythonpro.cohorts.models import Cohort


@pytest.fixture
def fake():
    return Faker('pt_BR')


@pytest.fixture
def client_with_user(client, logged_user):
    client.force_login(logged_user)
    return client


_all_roles = set('data_scientist lead client webdev bootcamper pythonista member'.split())
_advanced_roles = set('member pythonista bootcamper'.split())
_level_zero_roles = set('lead client webdev bootcamper member'.split())
_level_one_roles = set('client webdev bootcamper member'.split())
_level_two_roles = set('webdev bootcamper member'.split())
_level_three_roles = set('bootcamper member'.split())


@pytest.fixture
def logged_user(django_user_model):
    logged_user = baker.make(django_user_model, is_superuser=False)
    logged_user.email = logged_user.email.lower()
    logged_user.save()
    return logged_user


@pytest.fixture(params=_all_roles)
@pytest.mark.django_db
def pythonpro_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture
def client_with_all_roles(client, pythonpro_role):
    client.force_login(pythonpro_role)
    return client


@pytest.fixture(params=_advanced_roles)
@pytest.mark.django_db
def advanced_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture
def client_with_advanced_roles(client, advanced_role):
    client.force_login(advanced_role)
    return client


@pytest.fixture(params=_all_roles - _advanced_roles)
@pytest.mark.django_db
def not_advanced_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture(params=_level_one_roles)
@pytest.mark.django_db
def level_one_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture
def client_with_level_one_roles(client, level_one_role):
    client.force_login(level_one_role)
    return client


@pytest.fixture(params=_level_zero_roles)
@pytest.mark.django_db
def level_zero_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture
def client_with_level_zero_roles(client, level_zero_role):
    client.force_login(level_zero_role)
    return client


@pytest.fixture(params=_all_roles - _level_one_roles)
@pytest.mark.django_db
def not_level_one_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture
def client_with_not_level_one_roles(client, not_level_one_role):
    client.force_login(not_level_one_role)
    return client


@pytest.fixture(params=_level_two_roles)
@pytest.mark.django_db
def level_two_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture
def client_with_level_two_roles(client, level_two_role):
    client.force_login(level_two_role)
    return client


@pytest.fixture(params=_all_roles - _level_two_roles)
@pytest.mark.django_db
def not_level_two_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture
def client_with_not_level_two_roles(client, not_level_two_role):
    client.force_login(not_level_two_role)
    return client


@pytest.fixture(params=_level_three_roles)
@pytest.mark.django_db
def level_three_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture
def client_with_level_three_roles(client, level_three_role):
    client.force_login(level_three_role)
    return client


@pytest.fixture(params=_all_roles - _level_three_roles)
@pytest.mark.django_db
def not_level_three_role(logged_user, request):
    role = request.param
    assign_role(logged_user, role)
    return logged_user


@pytest.fixture
def client_with_not_level_three_roles(client, not_level_three_role):
    client.force_login(not_level_three_role)
    return client


@pytest.fixture
def cohort(db):
    return baker.make(Cohort)


@pytest.fixture
def client_with_lead(client, logged_user):
    assign_role(logged_user, 'lead')
    client.force_login(logged_user)
    return client


@pytest.fixture
def client_with_webdev(client, logged_user):
    assign_role(logged_user, 'webdev')
    client.force_login(logged_user)
    return client


@pytest.fixture
def client_with_member(client, logged_user):
    assign_role(logged_user, 'member')
    client.force_login(logged_user)
    return client


@pytest.fixture
def client_with_client(client, logged_user):
    assign_role(logged_user, 'client')
    client.force_login(logged_user)
    return client


@pytest.fixture
def client_with_bootcamper(client, logged_user):
    assign_role(logged_user, 'bootcamper')
    client.force_login(logged_user)
    return client


@pytest.fixture
def client_with_pythonista(client, logged_user):
    assign_role(logged_user, 'pythonista')
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
def turn_cache_off(settings):
    """
    This way test don't depend on local .env configuration
    """
    settings.CACHE_TURNED_ON = False


@pytest.fixture(autouse=True)
def turn_ssl_rediret_off_for_tests(settings):
    """
    There is no need to place secure=True in all client requests
    """
    settings.SECURE_SSL_REDIRECT = False


@pytest.fixture(autouse=True)
def turn_posthog_off_for_tests(settings):
    """
    There is no need to place secure=True in all client requests
    """
    posthog.disabled = True


pytest_plugins = ['pythonpro.modules.tests.test_topics_view']
