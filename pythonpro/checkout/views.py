import time
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlencode
from django_pagarme import facade
from django.utils import timezone

from pythonpro.checkout import facade as checkout_facade
from pythonpro.checkout import forms as checkout_forms
from pythonpro.checkout.forms import WaitingForm
from pythonpro.core.facade import is_client
from pythonpro.domain import user_facade


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

    login_url = reverse('two_factor:login')
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


@login_required
def webdev_landing_page_oto(request):
    template_name = 'checkout/webdev_landing_page_oto.html'
    return _webdev_landing_page_50_off(request, template_name)


@login_required
def webdev_landing_page_50_off(request):
    template_name = 'checkout/webdev_landing_page_50_off.html'
    return _webdev_landing_page_50_off(request, template_name, seconds_to_show_full_page=0)


def _webdev_landing_page_50_off(request, template_name, seconds_to_show_full_page=90):
    payment_item_config = facade.find_payment_item_config('webdev-oto')
    user = request.user
    if user.is_authenticated:
        data = {'name': user.first_name, 'email': user.email}
        form = facade.ContactForm(data)
    else:
        form = facade.ContactForm()

    countdown_limit = request.user.date_joined + timedelta(days=5)
    is_promotion_expired = timezone.now() > countdown_limit
    if request.GET.get('debug') is not None:
        is_promotion_expired = False

    ctx = {
        'payment_item_config': payment_item_config,
        'contact_form': form,
        'countdown_limit': countdown_limit,
        'is_promotion_expired': is_promotion_expired,
        'seconds_to_show_full_page': seconds_to_show_full_page
    }
    return render(request, template_name, ctx)


def webdev_landing_page(request):
    payment_item_config = facade.find_payment_item_config('webdev')

    user = request.user
    if user.is_authenticated:
        data = {'name': user.first_name, 'email': user.email, 'phone': ''}
        form = facade.ContactForm(data)
    else:
        form = facade.ContactForm()

    ctx = {
        'payment_item_config': payment_item_config,
        'contact_form': form,
    }
    return render(request, 'checkout/webdev_landing_page.html', ctx)
