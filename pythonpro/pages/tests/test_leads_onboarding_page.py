from django.urls import reverse


def test_should_return_200_when_load_invite_page(client):
    resp = client.get(reverse('pages:leads_onboarding_page'))
    assert resp.status_code == 200
