from datetime import datetime

import requests
from celery import shared_task
from django_pagarme import facade as django_pagarme_facade
from django_pagarme.models import PagarmePayment

from pythonpro import settings
from pythonpro.core import facade


def total_price(purchased_items):
    """
    Sum all items prices of purchase to return the total price
    :param purchased_items: itens of a givem purch
    :return total
    """
    total = 0
    for item in purchased_items:
        total += item.price
    return total / 100


@shared_task
def send_abandoned_cart(name, email, phone, payment_item_slug):
    """
    Send a potential client who filled their data but not complete the buy to hotzapp
    :param name: name filled at the form
    :param phone: phone filled at the form
    :param email: email filled at the form
    :param payment_item_slug: slug of the item of purchase
    """
    payment_config_item = django_pagarme_facade.get_payment_item(payment_item_slug)
    price = total_price([payment_config_item])
    potential_customer = {
        'created_at': datetime.now().isoformat(),
        'name': name,
        'phone': phone,
        'email': email,
        'currency_code_from': 'R$',
        'total_price': price,
        'line_items': [
            {
                'product_name': payment_config_item.name,
                'quantity': 1,
                'price': price
            }
        ],
    }
    return requests.post(settings.HOTZAPP_API_URL, json=potential_customer).status_code


PAYMENT_METHOD_DCT = {
    django_pagarme_facade.CREDIT_CARD: 'credit',
    django_pagarme_facade.BOLETO: 'billet',
}
STATUS_DCT = {
    django_pagarme_facade.REFUSED: 'refused',
    django_pagarme_facade.PAID: 'paid',
    django_pagarme_facade.WAITING_PAYMENT: 'issued',
}


@shared_task
def send_purchase_notification(payment_id):
    """
    Send a potential client who filled their data but not complete the buy-in face of a refused credit card
    :params payment_id: id of payment
    """
    payment = django_pagarme_facade.find_payment(payment_id)
    last_notification = payment.notifications.order_by('-creation').values('status', 'creation').first()
    payment_profile = django_pagarme_facade.get_user_payment_profile(payment.user_id)
    payment_config_items = payment.items.all()
    purchased_items = [{"product_name": item.name, "quantity": '1', "price": str(item.price / 100), } for item in
                       payment_config_items]

    purchase = {
        'created_at': last_notification['creation'].isoformat(),
        'transaction_id': payment.transaction_id,
        'name': payment_profile.name,
        'email': payment_profile.email,
        'phone': str(payment_profile.phone),
        'total_price': total_price(payment_config_items),
        'line_items': purchased_items,
        'payment_method': PAYMENT_METHOD_DCT[payment.payment_method],
        'financial_status': STATUS_DCT[last_notification['status']],
        'billet_url': payment.boleto_url,
        'billet_barcode': payment.boleto_barcode,

    }
    return requests.post(settings.HOTZAPP_API_URL, json=purchase).status_code


@shared_task
def verify_purchase(name, email, phone, payment_item_slug):
    """
    Verify each buy interaction to see if it succeeded and depending on each situation take an action
    :param name: name filled at the form
    :param phone: phone filled at the form
    :param email: email filled at the form
    :param payment_item_slug: slug of the item of purchase
    """
    try:
        user = facade.find_user_by_email(email=email)
    except facade.UserDoesNotExist:
        return send_abandoned_cart(name, email, phone, payment_item_slug)
    else:
        payment = PagarmePayment.objects.filter(user__id=user.id, items__slug__exact=payment_item_slug).order_by(
            '-id').first()
        if payment is None or payment.status() != django_pagarme_facade.PAID:
            return send_abandoned_cart(name, email, phone, payment_item_slug)
