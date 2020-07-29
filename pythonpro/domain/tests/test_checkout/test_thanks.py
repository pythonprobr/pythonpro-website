import pytest
from django.urls import reverse

from pythonpro.domain.tests.test_checkout.conftest import ALL_ACTIVE_PRODUCTS


@pytest.mark.parametrize('slug', ALL_ACTIVE_PRODUCTS)
def test_all_slugs_available(client, slug):
    resp = client.get(reverse('django_pagarme:thanks', kwargs={'slug': slug}))
    assert resp.status_code == 200
