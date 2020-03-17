# Setup django pagarme listener
from django_pagarme import facade as django_pagarme_facade

from pythonpro.core import facade as core_facade
from pythonpro.email_marketing import facade as email_marketing_facade


def contact_info_listener(name, email, phone, payment_item_slug, user=None):
    if (user is not None) and user.is_authenticated:
        user_id = user.id
        if 'pytools' in payment_item_slug:
            core_facade.client_checkout_form(user, 'unknown')
        elif 'membership' in payment_item_slug:
            core_facade.member_checkout_form(user)
    else:
        user_id = None
    email_marketing_facade.create_or_update_with_no_role.delay(
        name, email, payment_item_slug, id=user_id, phone=str(phone)
    )


django_pagarme_facade.add_contact_info_listener(contact_info_listener)
