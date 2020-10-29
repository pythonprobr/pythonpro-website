# Setup django pagarme listener
from celery import shared_task
from django_pagarme import facade as django_pagarme_facade

from pythonpro.core import facade as core_facade
from pythonpro.domain import user_domain
from pythonpro.domain.hotzapp_domain import verify_purchase, send_purchase_notification
from pythonpro.email_marketing import facade as email_marketing_facade

__all__ = ['contact_info_listener', 'user_factory', 'payment_handler_task', 'payment_change_handler']


def contact_info_listener(name: str, email: str, phone: str, payment_item_slug: str, user=None):
    if (user is not None) and user.is_authenticated:
        user_id = user.id
        if payment_item_slug.startswith('membership'):
            core_facade.member_checkout_form(user)
        elif payment_item_slug.startswith('webdev'):
            core_facade.webdev_checkout_form(user)
    else:
        user_id = None
    phone = str(phone)
    email_marketing_facade.create_or_update_with_no_role.delay(
        name, email, f'{payment_item_slug}-form', id=user_id, phone=phone
    )

    verify_purchase_after_30_minutes(name, email, phone, payment_item_slug)


def verify_purchase_after_30_minutes(name, email, phone, payment_item_slug):
    THIRTY_MINUTES_IN_SECONDS = 1800
    verify_purchase.apply_async((name, email, phone, payment_item_slug), countdown=THIRTY_MINUTES_IN_SECONDS)


django_pagarme_facade.add_contact_info_listener(contact_info_listener)


def user_factory(pagarme_transaction):
    customer = pagarme_transaction['customer']
    customer_email = customer['email'].lower()
    customer_first_name = customer['name'].split()[0]
    customer_phone = customer['phone_numbers'][0]
    return user_domain.force_register_lead(customer_first_name, customer_email, customer_phone)


django_pagarme_facade.set_user_factory(user_factory)


@shared_task
def payment_handler_task(payment_id):
    payment = django_pagarme_facade.find_payment(payment_id)
    try:
        slug = payment.first_item_slug()
    except django_pagarme_facade.PagarmePaymentItemDoesNotExist:
        pass  # no need to handle payment with no Item
    else:
        status = payment.status()
        if status == django_pagarme_facade.PAID:
            user = payment.user
            if payment.payment_method == django_pagarme_facade.BOLETO:
                email_marketing_facade.remove_tags.delay(user.email, user.id, f'{slug}-boleto', f'{slug}-refused')
            else:
                email_marketing_facade.remove_tags.delay(user.email, user.id, f'{slug}-refused')
            _promote(user, slug)
            if slug.startswith('bootcamp'):
                send_purchase_notification.delay(payment.id)
        elif status == django_pagarme_facade.REFUSED:
            user = payment.user
            email_marketing_facade.tag_as.delay(user.email, user.id, f'{slug}-refused')
            if slug.startswith('bootcamp'):
                send_purchase_notification.delay(payment.id)
        elif status == django_pagarme_facade.WAITING_PAYMENT:
            user = payment.user
            email_marketing_facade.tag_as.delay(user.email, user.id, f'{slug}-boleto')
            if slug.startswith('bootcamp'):
                send_purchase_notification.delay(payment.id)


def _promote(user, slug: str):
    if slug.startswith('membership'):
        user_domain.promote_member(user, 'unknown')
    elif slug == 'pacote-proximo-nivel-67-discount':
        user_domain.promote_pythonista(user, 'unknown')
    elif slug.startswith('webdev') or slug == 'treinamento-devpro-webinar':
        user_domain.promote_webdev(user, 'unknown')
    elif slug.startswith('data-science'):
        user_domain.promote_data_scientist(user, 'unknown')
    elif slug in {'bootcamp', 'bootcamp-webdev'}:
        user_domain.promote_bootcamper(user, 'unknown')
        user_domain.promote_pythonista(user, 'unknown')
    elif slug.startswith('bootcamp'):
        user_domain.promote_bootcamper(user, 'unknown')
    else:
        raise ValueError(f'{slug} should contain webdev or membership or data-science')


def payment_change_handler(payment_id):
    payment_handler_task.delay(payment_id)


django_pagarme_facade.add_payment_status_changed(payment_change_handler)


def availability_strategy(payment_item_config, request):
    if not payment_item_config.is_available():
        return False
    elif request.GET.get('debug', '').lower() == 'true':
        return True
    elif payment_item_config.slug.startswith('bootcamp-webdev'):
        return core_facade.is_webdev(request.user)
    return True


django_pagarme_facade.set_available_payment_config_item_strategy(availability_strategy)
