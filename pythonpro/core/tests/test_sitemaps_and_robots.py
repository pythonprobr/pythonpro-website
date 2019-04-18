import pytest
from django.test import Client
from django.urls import reverse


@pytest.fixture
def resp_sitemap(client: Client, db):
    return client.get(reverse('core:sitemap'), secure=True)


def test_sitemap_status_code(resp_sitemap):
    assert resp_sitemap.status_code == 200


@pytest.fixture
def resp_robots(client: Client, db):
    return client.get(reverse('core:robots'), secure=True)


def test_robots_status_code(resp_robots):
    assert resp_robots.status_code == 200
