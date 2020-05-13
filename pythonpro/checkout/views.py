import time

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.timezone import now
from django_pagarme import facade

from pythonpro.checkout import facade as checkout_facade
from pythonpro.checkout import forms as checkout_forms
from pythonpro.checkout.forms import WaitingForm
from pythonpro.core.facade import is_client
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


def pytools_oto_lp(request):
    is_debug = bool(request.GET.get('debug', False))
    user = request.user
    if not (user.is_authenticated or is_debug):
        return HttpResponseRedirect(reverse('checkout:pytools_lp'))

    slug = 'pytools-oto'
    if user.is_authenticated:
        user_facade.visit_client_landing_page(user, source=request.GET.get('utm_source', default='unknown'))
        data = {'name': user.first_name, 'email': user.email}
        form = facade.ContactForm(data)
    else:
        form = facade.ContactForm()
    countdown_limit = payment_facade.calculate_oto_expires_datetime(user.date_joined) if not is_debug else now()
    is_promotion_expired = not (is_debug or payment_facade.is_on_pytools_oto_season(user.date_joined))
    payment_item_config = facade.find_payment_item_config(slug)
    payment_form_config = payment_item_config.default_config
    price_float = payment_item_config.price / 100
    installments = payment_form_config.max_installments
    price_installment = payment_form_config.calculate_amount(payment_item_config.price, installments) / installments
    price_installment /= 100
    return render(
        request,
        'checkout/pytools_oto_lp.html', {
            'contact_form': form,
            'slug': slug,
            'payment_item_config': payment_item_config,
            'price_float': price_float,
            'price_installment': price_installment,
            'is_promotion_expired': is_promotion_expired,
            'countdown_limit': countdown_limit,
        })


def membership_lp(request):
    user = request.user

    if request.method == 'POST':
        form = WaitingForm(request.POST)
        if form.is_valid():
            source = request.GET.get('utm_source', default='unknown')
            data = form.cleaned_data
            if user.is_authenticated:
                user_facade.subscribe_to_waiting_list(request.user, data['phone'], source)
            else:
                user_facade.subscribe_anonymous_user_to_waiting_list(
                    data['email'], data['first_name'], data['phone'], source
                )
            return redirect(reverse('checkout:waiting_list_ty'))
        else:
            return render(request, 'checkout/membership_lp_subscription_closed.html', {'form': form})

    if user.is_authenticated:
        user_facade.visit_member_landing_page(request.user, source=request.GET.get('utm_source', default='unknown'))

    is_debug = bool(request.GET.get('debug', False))

    should_show_closed_subscription_page = not (is_debug or checkout_facade.is_launch_open())

    if should_show_closed_subscription_page:
        form = checkout_forms.WaitingForm()
        return render(request, 'checkout/membership_lp_subscription_closed.html', {'form': form})

    has_client_discount = False

    if user.is_authenticated:
        has_client_discount = is_client(user)
        data = {'name': user.first_name, 'email': user.email}
        form = facade.ContactForm(data)
    else:
        form = facade.ContactForm()

    has_first_day_discount = checkout_facade.is_launch_first_day_discount() or is_debug
    no_discount_item_config = facade.find_payment_item_config('membership')
    payment_item_config = no_discount_item_config
    client_discount = 0
    first_day_discount = 0
    client_discount_slug = 'membership-client'
    if has_first_day_discount:
        first_day_discount_item_config = facade.find_payment_item_config('membership-first-day')
        payment_item_config = first_day_discount_item_config
        first_day_discount = no_discount_item_config.price - first_day_discount_item_config.price
        if has_client_discount:
            client_discount_slug = 'membership-client-first-day'

    if has_client_discount:
        client_discount_item_config = facade.find_payment_item_config(client_discount_slug)
        payment_item_config = client_discount_item_config
        client_discount = no_discount_item_config.price - client_discount_item_config.price - first_day_discount

    login_url = reverse('login')
    redirect_path = reverse('checkout:membership_lp')
    qs = urlencode({'utm_source': request.GET.get('utm_source', 'unknown')})
    redirect_url = f'{redirect_path}?{qs}'
    qs = urlencode({'next': redirect_url})
    login_url = f'{login_url}?{qs}'

    promotion_end_date = (
        checkout_facade.discount_datetime_limit if has_first_day_discount else checkout_facade.launch_datetime_finish
    )

    # Seconds to milliseconds https://stackoverflow.com/questions/5022447/converting-date-from-python-to-javascript
    promotion_end_date_milliseconds = int(time.mktime(promotion_end_date.timetuple())) * 1000

    context = {
        'launch_datetime_finish': checkout_facade.launch_datetime_finish,
        'discount_datetime_limit': checkout_facade.discount_datetime_limit,
        'payment_item_config': payment_item_config,
        'contact_form': form,
        'login_url': login_url,
        'has_first_day_discount': has_first_day_discount,
        'has_client_discount': has_client_discount,
        'client_discount': client_discount,
        'first_day_discount': first_day_discount,
        'promotion_end_date': promotion_end_date,
        'promotion_end_date_milliseconds': promotion_end_date_milliseconds,
        'no_discount_item_config': no_discount_item_config,
    }
    return render(request, 'checkout/membership_lp_subscription_open.html', context)


def waiting_list_ty(request):
    return render(request, 'checkout/waiting_list_ty.html', {'email': request.user.email})
