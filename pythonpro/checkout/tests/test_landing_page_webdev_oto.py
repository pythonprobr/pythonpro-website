import pytest

from django.urls import reverse


@pytest.fixture
def resp(client, db):
    return client.get(reverse('webdev_landing_page'), secure=True)


def test_should_page_exists(resp):
    assert resp.status_code == 200
