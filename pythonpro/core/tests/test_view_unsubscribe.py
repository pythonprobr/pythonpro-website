from django.urls import reverse


def test_status_code(client):
    assert client.get(reverse('core:unsubscribe'))
