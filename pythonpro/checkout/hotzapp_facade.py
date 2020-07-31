from datetime import datetime

import pytz
import requests
from celery import shared_task
from django_pagarme import facade as django_pagarme_facade

from pythonpro import settings
from pythonpro.core import facade


def current_time_with_timezone():
    """
    Return the current time in ISO format and with timezone
    """
    time_zone = pytz.timezone("America/Sao_Paulo")
    aware_dt = time_zone.localize(datetime.now())
    return aware_dt.isoformat()


def total_price(purchased_items):
    """
    Sum all items prices of purchase to return the total price
    :param purchased_items: itens of a givem purch
    :return total
    """
    total = 0
    for item in purchased_items:
        total += item.price
    return str(total / 100)


@shared_task
def send_abandoned_cart(name, email, phone, payment_item_slug):
    """
    Send a potential client who filled their data but not complete the buy to hotzapp
    :param name: name filled at the form
    :param phone: phone filled at the form
    :param email: email filled at the form
    :param payment_item_slug: slug of the item of purchase
    """
    potential_customer = {
        "created_at": current_time_with_timezone(),
        "name": name,
        "phone": phone,
        "email": email,
        "currency_code_from": 'R$',
        "total_price": "0",
        "line_items": [
            {
                "product_name": payment_item_slug,
                "quantity": '1',
                "price": "0",
            }
        ],
    }
    return requests.post(settings.HOTZAPP_API_URL, potential_customer)


@shared_task
def send_paid_purchase(payment_id):
    """
    Send a potential client who filled their data but not complete the buy-in face of a billet not paid
    :params payment_id: id of payment
    """
    payment = django_pagarme_facade.find_payment(payment_id)
    purchased_items = [{"product_name": item.name, "quantity": '1', "price": str(item.price / 100), } for item in
                       payment.items.all()]

    potential_customer = {
        "created_at": current_time_with_timezone(),
        "transaction_id": payment.transaction_id,
        "name": payment.user.name,
        "phone": None,  # How to recovery user phone?
        "email": payment.user.email,
        "currency_code_from": 'R$',
        "total_price": total_price(purchased_items),
        "line_items": purchased_items,
        "payment_method": 'credit',
        "financial_status": 'paid',
        "paid_at": current_time_with_timezone(),
    }
    return requests.post(settings.HOTZAPP_API_URL, potential_customer)


@shared_task
def send_billet_issued(payment_id):
    """
    Send a potential client who filled their data but not complete the buy-in face of a billet not paid
    :params payment_id: id of payment
    """
    payment = django_pagarme_facade.find_payment(payment_id)

    purchased_items = [{"product_name": item.name, "quantity": '1', "price": str(item.price / 100), } for item in
                       payment.items.all()]

    potential_customer = {
        "created_at": current_time_with_timezone(),
        "transaction_id": payment.transaction_id,
        "name": payment.user.name,
        "email": payment.user.email,
        "phone": None,
        "total_price": total_price(purchased_items),
        "line_items": purchased_items,
        "payment_method": 'billet',
        "financial_status": 'issued',
    }
    return requests.post(settings.HOTZAPP_API_URL, potential_customer)


@shared_task
def send_refused_credit_card(payment_id):
    """
    Send a potential client who filled their data but not complete the buy-in face of a refused credit card
    :params payment_id: id of payment
    """
    payment = django_pagarme_facade.find_payment(payment_id)

    purchased_items = [{"product_name": item.name, "quantity": '1', "price": str(item.price / 100), } for item in
                       payment.items.all()]
    potential_customer = {
        "created_at": current_time_with_timezone(),
        "transaction_id": payment.transaction_id,
        "name": payment.user.name,
        "email": payment.user.email,
        "phone": None,  ###
        "total_price": total_price(purchased_items),
        "line_items": purchased_items,
        "payment_method": 'credit',
        "financial_status": 'refused',
    }
    return requests.post(settings.HOTZAPP_API_URL, potential_customer)


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
        send_abandoned_cart(name, phone, email, payment_item_slug)
    else:
        pass
