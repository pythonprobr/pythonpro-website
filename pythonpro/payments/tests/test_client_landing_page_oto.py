from django.urls import reverse


def test_should_redirect_to_normal_client_landing_page_when_user_is_not_logged(client):
    resp = client.get(reverse('payments:client_landing_page_oto'), secure=True)
    assert resp.status_code == 301
    assert resp.url == reverse('checkout:pytools_oto_lp')


def test_should_redirect_to_normal_client_landing_page_when_user_is_logged(client_with_lead):
    resp = client_with_lead.get(reverse('payments:client_landing_page_oto'), secure=True)
    assert resp.status_code == 301
    assert resp.url == reverse('checkout:pytools_oto_lp')
