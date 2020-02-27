import pytest
from django.urls import reverse


@pytest.fixture
def resp(client):
    return client.get(reverse('core:linktree'), secure=True)


def test_status_code(resp):
    assert 200 == resp.status_code
