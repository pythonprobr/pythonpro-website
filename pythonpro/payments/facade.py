from datetime import datetime, timedelta
from typing import Tuple

import pagarme as _pagarme
from dateutil.relativedelta import MO, relativedelta
from django.conf import settings
from django.utils.timezone import now

_pagarme.authentication_key(settings.PAGARME_API_KEY)

PYTOOLS_PRICE = 39700
PYTOOLS_PROMOTION_PRICE = 9700  # flashning launch
PYTOOLS_OTO_PRICE = 9700  # one time offer in python birds thank you page
PYTOOLS_DO_PRICE = 19700  # done offer for people who finished python birds
MEMBERSHIP_PRICE = 159990
MEMBERSHIP_DISCOUNT_FOR_CLIENTS = 10000


def _discover_pytools_price(user_creation: datetime, item_id=''):
    price = PYTOOLS_PRICE
    if item_id.startswith('pytools-do'):
        price = PYTOOLS_DO_PRICE
    elif is_on_pytools_oto_season(user_creation):
        price = PYTOOLS_OTO_PRICE
    elif is_on_pytools_promotion_season(user_creation):
        price = PYTOOLS_PROMOTION_PRICE

    return price


class PagarmeValidationException(Exception):
    pass


class PagarmeNotPaidTransaction(Exception):
    pass


def membership_capture(price: int, token: str):
    amount = _pagarme.transaction.find_by_id(token)['amount']
    if amount < price:
        raise PagarmeValidationException(f'Payment done ({amount}) is less then price ({price}) for token: {token}')
    return _pagarme.transaction.capture(token, {'amount': amount})


def confirm_membership_boleto_payment(user_id: int, notification: dict, raw_post: str, expected_signature: str) -> dict:
    transaction = extract_transaction(notification, raw_post, expected_signature)
    item_id = transaction['items'][0]['id']
    # id is generated concatenating Module slug and user's id. Check content_membership_landing_page pagarme JS
    expected_id = f'membership-{user_id}'
    if item_id != expected_id:
        raise PagarmeValidationException(f"Expected item's id {expected_id} differs from {item_id}", notification)
    return transaction


def extract_transaction(notification: dict, raw_post: str, expected_signature):
    if not _pagarme.postback.validate(expected_signature, raw_post):
        raise PagarmeValidationException(notification, expected_signature)
    if notification['object'] != 'transaction' or notification['current_status'] != 'paid':
        raise PagarmeNotPaidTransaction()
    return _pagarme.transaction.find_by_id(notification['transaction[id]'])


def calculate_pytools_promotion_interval() -> Tuple[datetime, datetime]:
    """
    calculate promotion interval for this week based on time. Promotion will begin on monday and stop on Thursday
    :return:
    """
    now_dt = now()
    this_week_monday = now_dt + relativedelta(weekday=MO(-1), hour=0, minute=0, second=0)
    this_week_thursday = this_week_monday + relativedelta(days=5, hour=23, minute=59, second=59)
    return this_week_monday, this_week_thursday


def is_on_pytools_promotion_season(creation: datetime) -> bool:
    """
    Calculate if is period of promotion which is 7 weeks after creation
    :param creation: datetime of creation
    :return: boolean indication if its os promotion period or not
    """
    creation_begin, creation_end = calculate_7th_week_before_promotion()
    return creation_begin <= creation <= creation_end


def calculate_7th_week_before_promotion() -> Tuple[datetime, datetime]:
    """
    Calculate 7th week before promotion. Useful to know user created on that period
    :return: Tuple where first item is the interval's begin and second is the interval's end
    """
    promotion_begin, _ = calculate_pytools_promotion_interval()
    creation_begin = promotion_begin + relativedelta(weekday=MO(-8))
    creation_end = creation_begin + relativedelta(days=6, hour=23, minute=59, second=59)
    return creation_begin, creation_end


def calculate_oto_expires_datetime(user_creation: datetime) -> datetime:
    """
    Calculate datetime expiration for OTO pytools offer.
    :return: datetime
    """
    return user_creation + timedelta(minutes=30)


def is_on_pytools_oto_season(user_creation: datetime) -> bool:
    """
    Chekc if user is available to receive Pytools OTO.
    :return: boolean
    """
    return calculate_oto_expires_datetime(user_creation) > now()
