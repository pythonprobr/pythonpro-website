from datetime import datetime
from typing import Tuple

import pagarme as _pagarme
from dateutil.relativedelta import MO, relativedelta
from django.conf import settings
from django.utils.timezone import now

_pagarme.authentication_key(settings.PAGARME_API_KEY)
PYTOOLS_PRICE = 9999
PYTOOLS_PROMOTION_PRICE = 4999


def pytools_capture(token: str, user_creation: datetime):
    price = PYTOOLS_PROMOTION_PRICE if is_on_pytools_promotion_season(user_creation) else PYTOOLS_PRICE
    return _pagarme.transaction.capture(token, {'amount': price})


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
