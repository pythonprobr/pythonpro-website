# Setup django pagarme listener
from celery import shared_task
from django_pagarme import facade as django_pagarme_facade

from pythonpro.core import facade as core_facade
from pythonpro.domain import user_facade
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
    email_marketing_facade.create_or_update_with_no_role.delay(
        name, email, f'{payment_item_slug}-form', id=user_id, phone=str(phone)
    )


django_pagarme_facade.add_contact_info_listener(contact_info_listener)


def user_factory(pagarme_transaction):
    customer = pagarme_transaction['customer']
    customer_email = customer['email'].lower()
    customer_first_name = customer['name'].split()[0]
    return user_facade.force_register_lead(customer_first_name, customer_email)


django_pagarme_facade.set_user_factory(user_factory)

GENERATED_BOLETO_TAG = 'generated-boleto'


@shared_task()
def payment_handler_task(payment_id):
    payment = django_pagarme_facade.find_payment(payment_id)
    status = payment.status()
    slug = payment.first_item_slug()
    if status == django_pagarme_facade.PAID:
        user = payment.user
        if payment.payment_method == django_pagarme_facade.BOLETO:
            email_marketing_facade.remove_tags.delay(user.email, user.id, f'{slug}-boleto')
        _promote(user, slug)
    elif status == django_pagarme_facade.WAITING_PAYMENT:
        user = payment.user
        email_marketing_facade.tag_as.delay(user.email, user.id, f'{slug}-boleto')


def _promote(user, slug: str):
    if slug.startswith('membership'):
        user_facade.promote_member(user, 'unknown')
    elif slug.startswith('webdev'):
        user_facade.promote_webdev(user, 'unknown')
    elif slug.startswith('data-science'):
        user_facade.promote_data_scientist(user, 'unknown')
    else:
        raise ValueError(f'{slug} should contain webdev or membership')


def payment_change_handler(payment_id):
    payment_handler_task.delay(payment_id)


django_pagarme_facade.add_payment_status_changed(payment_change_handler)
