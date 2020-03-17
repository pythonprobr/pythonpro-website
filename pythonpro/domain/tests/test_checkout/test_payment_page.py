import pytest
from django.urls import reverse

all_slugs = pytest.mark.parametrize(
    'slug',
    [
        'pytools',
        'pytools-oto',
        'pytools-done',
        'membership',
        'membership-client',
        'membership-client-first-day',
        'membership-first-day',
    ]
)


@all_slugs
def test_all_slugs_available(client, slug):
    resp = client.get(reverse('django_pagarme:pagarme', kwargs={'slug': slug}), secure=True)
    assert resp.status_code == 200
