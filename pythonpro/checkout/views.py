from django.shortcuts import render
from django.utils.timezone import now
from django_pagarme import facade

from pythonpro.domain import user_facade
from pythonpro.payments import facade as payment_facade


def pytools_lp(request):
    user = request.user
    slug = 'pytools'
    if user.is_authenticated:
        user_facade.visit_client_landing_page(user, source=request.GET.get('utm_source', default='unknown'))
        data = {'name': user.first_name, 'email': user.email}
        form = facade.ContactForm(data)
    else:
        form = facade.ContactForm()
    user_creation = user.date_joined if user.is_authenticated else now()
    is_promotion_season = payment_facade.is_on_pytools_promotion_season(user_creation)
    payment_item_config = facade.find_payment_item_config(slug)
    payment_form_config = payment_item_config.default_config
    price_float = payment_item_config.price / 100
    installments = payment_form_config.max_installments
    price_installment = payment_form_config.calculate_amount(payment_item_config.price, installments) / installments
    price_installment /= 100
    _, promotion_end_date = payment_facade.calculate_pytools_promotion_interval()
    return render(
        request,
        'checkout/pytools_lp.html', {
            'contact_form': form,
            'slug': slug,
            'payment_item_config': payment_item_config,
            'price_float': price_float,
            'price_installment': price_installment,
            'is_promotion_season': is_promotion_season,
            'promotion_end_date': promotion_end_date,
            'is_promotion_expired': False,
        })
