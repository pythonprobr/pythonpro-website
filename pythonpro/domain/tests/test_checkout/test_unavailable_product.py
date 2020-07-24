from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from django_pagarme import facade
from django_pagarme.models import PagarmeItemConfig

from pythonpro.django_assertions import dj_assert_redirects


@pytest.fixture
def unavailable_config():
    cfg = facade.get_payment_item('pytools')
    cfg.available_until = timezone.now() - timedelta(seconds=1)
    cfg.save()
    return cfg


def test_unavailable_on_db(client, unavailable_config):
    assert_unavailable(client, [unavailable_config])


def test_webdev_discount_not_available(client_with_not_level_two_roles):
    qs = PagarmeItemConfig.objects.filter(slug__startswith='bootcamp-webdev')
    assert qs.count() == 3
    assert_unavailable(client_with_not_level_two_roles, qs)


def test_webdev_discount_available_with_debug(client_with_webdev):
    qs = PagarmeItemConfig.objects.filter(slug__startswith='bootcamp-webdev')
    for pagarme_item_config in qs:
        slug_kwargs_args = {'slug': pagarme_item_config.slug}
        path = reverse('django_pagarme:pagarme', kwargs=slug_kwargs_args)
        path += '?debug=true'
        resp = client_with_webdev.get(path)
        assert resp.status_code == 200


def assert_unavailable(client, qs):
    for pagarme_item_config in qs:
        slug_kwargs_args = {'slug': pagarme_item_config.slug}
        path = reverse('django_pagarme:pagarme', kwargs=slug_kwargs_args)
        resp = client.get(path)
        dj_assert_redirects(resp, reverse('django_pagarme:unavailable', kwargs=slug_kwargs_args))
