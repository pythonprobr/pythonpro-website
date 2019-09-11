from django.urls import reverse
from django.utils.http import urlencode

from pythonpro.core import facade as _core_facade
from pythonpro.core.models import User as _User
from pythonpro.domain import user_facade as _user_facade
from pythonpro.payments import facade as _payment_facade
from pythonpro.payments.facade import PagarmeNotPaidTransaction, PagarmeNotPaidTransaction as _PagarmeNotPaidTransaction

__all__ = ['calculate_membership_price', 'subscribe_anonymous_member_who_paid_boleto',
           'subscribe_member_who_paid_boleto', 'capture_payment']


def calculate_membership_price(user: _User) -> int:
    """
    Calculate membership price based on user role. Clients have discount
    :param user:
    :return: integer representing price in BRL cents
    """
    discount = _payment_facade.MEMBERSHIP_DISCOUNT_FOR_CLIENTS if _core_facade.is_client(user) else 0

    return _payment_facade.MEMBERSHIP_PRICE - discount


def subscribe_member_who_paid_boleto(user_id: int, notification_data: dict, raw_post: str, signature: str,
                                     source: str = 'unknow') -> _User:
    try:
        _payment_facade.confirm_membership_boleto_payment(user_id, notification_data, raw_post, signature)
    except _PagarmeNotPaidTransaction:
        pass
    else:
        user = _user_facade.find_user_by_id(user_id)
        _user_facade.promote_member(user, source)
        return user


def subscribe_anonymous_member_who_paid_boleto(
        notification_data: dict, raw_post: str, signature: str, source: str = 'unknow') -> _User:
    try:
        transaction = _payment_facade.extract_transaction(notification_data, raw_post, signature)
    except PagarmeNotPaidTransaction:
        pass  # No problem, we need to handle only paid transactions
    else:
        user = _user_facade.find_user_by_email(transaction['customer']['email'])
        _user_facade.promote_member(user, source)
        return user


def capture_payment(token, user, source='unknow'):
    pagarme_resp = _payment_facade.membership_capture(calculate_membership_price(user), token)
    customer = pagarme_resp['customer']
    customer_email = customer['email']
    customer_first_name = customer['name'].split()[0]
    payment_method = pagarme_resp['payment_method']
    if payment_method == 'credit_card':
        if user.is_authenticated:
            _user_facade.promote_member(user, source)
        else:
            _user_facade.force_register_member(customer_first_name, customer_email, source)
        dct = {'redirect_url': reverse('payments:membership_thanks')}
    elif payment_method == 'boleto':
        if not user.is_authenticated:
            user = _user_facade.force_register_lead(customer_first_name, customer_email, source)
        _user_facade.member_generated_boleto(user)
        path = reverse('payments:membership_boleto')
        qs = urlencode({k: pagarme_resp[k] for k in ['boleto_barcode', 'boleto_url']})
        dct = {'redirect_url': f'{path}?{qs}'}
    else:
        raise ValueError(f'Invalid payment method {payment_method}')
    return dct
