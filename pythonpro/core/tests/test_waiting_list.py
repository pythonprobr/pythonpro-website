from django.urls import reverse


def test_ty_status(client):
    resp = client.get(
        reverse(viewname='core:waiting_list'),
    )
    assert 200 == resp.status_code
