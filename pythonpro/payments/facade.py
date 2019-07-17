import pagarme as _pagarme
from django.conf import settings

_pagarme.authentication_key(settings.PAGARME_API_KEY)
PYTOOLS_PRICE = 9999


def pytools_capture(token: str):
    return _pagarme.transaction.capture(token, {'amount': PYTOOLS_PRICE})


class PagarmeValidationException(Exception):
    pass


class PagarmeNotPaidTransaction(Exception):
    pass


def confirm_boleto_payment(user_id, notification: dict, raw_post: str, expected_signature):
    transaction = extract_transaction(notification, raw_post, expected_signature)
    item_id = transaction['items'][0]['id']
    # id is generated concatenating Module slug and user's id. Check content_client_landing_page pagarme JS
    expected_id = f'pytools-{user_id}'
    if item_id != expected_id:
        raise PagarmeValidationException(f"Expected item's id {expected_id} differs from {item_id}", notification)
    return transaction


def extract_transaction(notification: dict, raw_post: str, expected_signature):
    if not _pagarme.postback.validate(expected_signature, raw_post):
        raise PagarmeValidationException(notification, expected_signature)
    if notification['object'] != 'transaction' or notification['current_status'] != 'paid':
        raise PagarmeNotPaidTransaction()
    return _pagarme.transaction.find_by_id(notification['transaction[id]'])
