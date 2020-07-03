import pytest
from django.urls import reverse


@pytest.fixture
def resp(client):
    return client.get(reverse('core:linktree'))


def test_status_code(resp):
    assert 200 == resp.status_code
