from pythonpro.checkout.hotzapp_facade import send_abandoned_cart, send_refused_credit_card


def test_send_abandoned_cart():
    resp = send_abandoned_cart(name='User test', email='User@test.com', phone=5563432343,
                               payment_item_slug='DJANGO-PRO')
    assert resp.status_code == 200


def test_send_refused_credit_card():
    resp = send_refused_credit_card(name='User test', email='User@test.com', phone=5563432343,
                                    payment_item_slug='DJANGO-PRO')
    assert resp.status_code == 200
