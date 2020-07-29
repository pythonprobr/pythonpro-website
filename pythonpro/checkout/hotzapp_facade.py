from json.decoder import JSONDecodeError

import requests
from celery import shared_task

from pythonpro import settings
from pythonpro.core.models import User

run_until_available = shared_task(autoretry_for=(JSONDecodeError,), retry_backoff=True, max_retries=None)


@run_until_available
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


@run_until_available
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


@run_until_available
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


@run_until_available
def verify_purchase(name, email, phone, payment_item_slug):
    """
    Verify each buy interaction to see if it succeeded and depending on each situation take an action
    :param name: name filled at the form
    :param phone: phone filled at the form
    :param email: email filled at the form
    :param payment_item_slug: slug of the item of purchase
    """
    user = User.objects.get(email=email)
    if user is not None:
        pass
        # Usuário pode já existir e tentar comprar outro produto, mas nao finaliza a compra?
        # Usuário criado, compra realizada não é necessária a interação com hotzapp
        # o Hotzap vai ser usado só para usuários novos?

    send_abandoned_cart(name, phone, email, payment_item_slug)
