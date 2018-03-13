import pytest
from django.urls import reverse
from model_mommy import mommy


@pytest.fixture
def resp(client, django_user_model):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return client.get(reverse('sections:detail', kwargs={'slug': 'procedural'}))


def test_status_code(resp):
    assert resp.status_code == 200
