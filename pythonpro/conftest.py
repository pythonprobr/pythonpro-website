import pytest
from faker import Faker
from model_mommy import mommy


@pytest.fixture
def fake():
    return Faker('pt_BR')


@pytest.fixture
def client_with_user(client, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client
