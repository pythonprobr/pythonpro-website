from django.urls import reverse


def test_status_code(client):
    return client.get(reverse('core:unsubscribe'))
