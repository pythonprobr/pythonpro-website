import requests
from celery import shared_task

from pythonpro import settings
from pythonpro.core import facade


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
        "name": name,
        "email": email,
        "phone": phone,
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
def send_billet_issued(name, email, phone, payment_item_slug):
    """
    Send a potential client who filled their data but not complete the buy-in face of a billet not paid
    :param name: name filled at the form
    :param phone: phone filled at the form
    :param email: email filled at the form
    :param payment_item_slug: slug of the item of purchase
    """
    potential_customer = {
        "name": name,
        "email": email,
        "phone": phone,
        "line_items": [
            {
                "product_name": payment_item_slug,
                "quantity": '1',
                "price": "0",
            }
        ],
        "payment_method": 'billet',
        "financial_status": 'issued',
    }
    return requests.post(settings.HOTZAPP_API_URL, potential_customer)


@shared_task
def send_refused_credit_card(name, email, phone, payment_item_slug):
    """
    Send a potential client who filled their data but not complete the buy-in face of a refused credit card
    :param name: name filled at the form
    :param phone: phone filled at the form
    :param email: email filled at the form
    :param payment_item_slug: slug of the item of purchase
    """
    potential_customer = {
        "name": name,
        "email": email,
        "phone": phone,
        "line_items": [
            {
                "product_name": payment_item_slug,
                "quantity": '1',
                "price": "0",
            }
        ],
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



