import pytest
from faker import Faker
from model_mommy import mommy
from rolepermissions.roles import assign_role


@pytest.fixture
def fake():
    return Faker('pt_BR')


@pytest.fixture
def client_with_user(client, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client


@pytest.fixture
def client_with_lead(client, django_user_model):
    user = mommy.make(django_user_model)
    assign_role(user, 'lead')
    client.force_login(user)
    return client


@pytest.fixture
def client_with_member(client, django_user_model):
    user = mommy.make(django_user_model)
    assign_role(user, 'member')
    client.force_login(user)
    return client


@pytest.fixture
def client_with_client(client, django_user_model):
    user = mommy.make(django_user_model)
    assign_role(user, 'client')
    client.force_login(user)
    return client
