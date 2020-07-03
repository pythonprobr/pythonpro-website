from django.urls import reverse


def test_should_redirect_oto_to_bootcamp_landing_page(client):
    resp = client.get(reverse('payments:client_landing_page_oto'))
    assert resp.status_code == 302
    assert resp.url == reverse('member_landing_page')


def test_should_redirect_do_to_bootcamp_landing_page(client):
    resp = client.get(reverse('payments:client_landing_page_do'))
    assert resp.status_code == 302
    assert resp.url == reverse('member_landing_page')


def test_should_redirect_old_client_lp_to_bootcamp_landing_page(client):
    resp = client.get(reverse('payments:client_landing_page'))
    assert resp.status_code == 302
    assert resp.url == reverse('member_landing_page')
