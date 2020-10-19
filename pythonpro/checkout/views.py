import time
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django_pagarme import facade

from pythonpro.checkout import facade as checkout_facade
from pythonpro.checkout import forms as checkout_forms
from pythonpro.checkout.forms import WaitingForm
from pythonpro.core.facade import is_webdev
from pythonpro.domain import user_domain


def _redirect_to_bootcamp_lp(request):
    if checkout_facade.has_50_percent_discount():
        path_name = 'checkout:bootcamp_lp_d1'
    elif checkout_facade.has_35_percent_discount():
        path_name = 'checkout:bootcamp_lp_d2'
    else:
        path_name = 'checkout:bootcamp_lp_d3'
    if is_webdev(request.user):
        path_name = f'{path_name}_webdev'
    if not checkout_facade.is_launch_open():
        path_name = 'checkout:bootcamp_lp'
    return HttpResponseRedirect(reverse(path_name) + '?' + request.META['QUERY_STRING'])


def bootcamp_lp(request):
    if request.method == 'POST':
        form = WaitingForm(request.POST)
        if form.is_valid():
            source = request.GET.get('utm_source', default='unknown')
            data = form.cleaned_data
            session_id = request.session.session_key
            if request.user.is_authenticated:
                user_domain.subscribe_to_waiting_list(session_id, request.user, data['phone'], source)
            else:
                user_domain.subscribe_anonymous_user_to_waiting_list(
                    session_id, data['email'], data['first_name'], data['phone'], source
                )
            return redirect(reverse('checkout:waiting_list_ty'))
        return render(request, 'checkout/bootcamp_lp_subscription_closed.html', {'form': form})

    if not checkout_facade.is_launch_open():
        if request.user.is_authenticated:
            user_domain.visit_member_landing_page(request.user, source=request.GET.get('utm_source', default='unknown'))

        form = checkout_forms.WaitingForm()
        return render(request, 'checkout/bootcamp_lp_subscription_closed.html', {'form': form})

    return _redirect_to_bootcamp_lp(request)


def _no_wevdev_discount(request, discount_slug, promotion_end_date,
                        template_name='checkout/bootcamp_lp_subscription_open.html'):
    if request.user.is_authenticated:
        user_domain.visit_member_landing_page(request.user, source=request.GET.get('utm_source', default='unknown'))

    form = facade.ContactForm()
    payment_item_config = facade.find_payment_item_config(discount_slug)
    no_discount_item_config = facade.find_payment_item_config('bootcamp')
    first_day_discount = no_discount_item_config.price - payment_item_config.price
    client_discount = 0
    has_first_day_discount = True
    has_client_discount = False
    return _render_bootcamp_lp(client_discount, first_day_discount, form, has_client_discount, has_first_day_discount,
                               no_discount_item_config, payment_item_config, promotion_end_date, request, template_name)


def _render_bootcamp_lp(client_discount, first_day_discount, form, has_client_discount, has_first_day_discount,
                        no_discount_item_config, payment_item_config, promotion_end_date, request,
                        template_name='checkout/bootcamp_lp_subscription_open.html'):
    # Seconds to milliseconds https://stackoverflow.com/questions/5022447/converting-date-from-python-to-javascript
    promotion_end_date_milliseconds = int(time.mktime(promotion_end_date.timetuple())) * 1000
    context = {
        'launch_datetime_finish': checkout_facade.launch_datetime_finish,
        'discount_datetime_limit': promotion_end_date,
        'payment_item_config': payment_item_config,
        'contact_form': form,
        'has_first_day_discount': has_first_day_discount,
        'has_client_discount': has_client_discount,
        'client_discount': client_discount,
        'first_day_discount': first_day_discount,
        'promotion_end_date': promotion_end_date,
        'promotion_end_date_milliseconds': promotion_end_date_milliseconds,
        'no_discount_item_config': no_discount_item_config,
    }
    return render(request, template_name, context)


def bootcamp_lp_d1(request):
    user = request.user
    is_debug = bool(request.GET.get('debug', False))
    if not is_debug and ((not checkout_facade.has_50_percent_discount()) or is_webdev(user)):
        return _redirect_to_bootcamp_lp(request)

    return _no_wevdev_discount(
        request,
        'bootcamp-50-discount',
        checkout_facade.discount_50_percent_datetime_limit,
        'checkout/bootcamp_lp_d1.html'
    )


@login_required
def bootcamp_lp_d1_webdev(request):
    user = request.user
    is_debug = bool(request.GET.get('debug', False))
    if not is_debug and not (checkout_facade.has_50_percent_discount() and is_webdev(user)):
        return _redirect_to_bootcamp_lp(request)

    client_discount_slug = 'bootcamp-webdev-50-discount'
    first_day_discount_slug = 'bootcamp-50-discount'
    promotion_end_date = checkout_facade.discount_50_percent_datetime_limit

    return _render_with_webdev_and_first_day_discounts(
        request,
        client_discount_slug,
        first_day_discount_slug,
        promotion_end_date,
        'checkout/bootcamp_lp_d1.html'
    )


def bootcamp_lp_d2(request):
    user = request.user
    is_debug = bool(request.GET.get('debug', False))
    if not is_debug and (not checkout_facade.has_35_percent_discount() or is_webdev(user)):
        return _redirect_to_bootcamp_lp(request)

    return _no_wevdev_discount(
        request,
        'bootcamp-35-discount',
        checkout_facade.discount_35_percent_datetime_limit,
        'checkout/bootcamp_lp_d2.html'
    )


@login_required
def bootcamp_lp_d2_webdev(request):
    user = request.user
    is_debug = bool(request.GET.get('debug', False))
    if not is_debug and not (checkout_facade.has_35_percent_discount() and is_webdev(user)):
        return _redirect_to_bootcamp_lp(request)
    client_discount_slug = 'bootcamp-webdev-35-discount'
    first_day_discount_slug = 'bootcamp-35-discount'
    promotion_end_date = checkout_facade.discount_35_percent_datetime_limit

    return _render_with_webdev_and_first_day_discounts(
        request,
        client_discount_slug,
        first_day_discount_slug,
        promotion_end_date,
        'checkout/bootcamp_lp_d2.html'
    )


def bootcamp_lp_d3(request):
    user = request.user
    has_discount = checkout_facade.has_35_percent_discount() or checkout_facade.has_50_percent_discount() or is_webdev(
        user)
    is_debug = bool(request.GET.get('debug', False))
    if not is_debug and ((not checkout_facade.is_launch_open()) or has_discount):
        return _redirect_to_bootcamp_lp(request)

    if request.user.is_authenticated:
        user_domain.visit_member_landing_page(request.user, source=request.GET.get('utm_source', default='unknown'))

    form = facade.ContactForm()
    payment_item_config = no_discount_item_config = facade.find_payment_item_config('bootcamp')
    first_day_discount = 0
    client_discount = 0
    has_first_day_discount = False
    has_client_discount = False
    promotion_end_date = checkout_facade.launch_datetime_finish
    return _render_bootcamp_lp(
        client_discount,
        first_day_discount,
        form,
        has_client_discount,
        has_first_day_discount,
        no_discount_item_config,
        payment_item_config,
        promotion_end_date,
        request,
        'checkout/bootcamp_lp_d3.html'
    )


@login_required
def bootcamp_lp_d3_webdev(request):
    user = request.user
    has_discount = checkout_facade.has_35_percent_discount() or checkout_facade.has_50_percent_discount()
    is_debug = bool(request.GET.get('debug', False))
    if not is_debug and (has_discount or not (checkout_facade.is_launch_open() and is_webdev(user))):
        return _redirect_to_bootcamp_lp(request)

    user_domain.visit_member_landing_page(request.user, source=request.GET.get('utm_source', default='unknown'))
    has_client_discount = True
    data = {'name': request.user.first_name, 'email': request.user.email}
    form = facade.ContactForm(data)
    has_first_day_discount = False
    no_discount_item_config = facade.find_payment_item_config('bootcamp')
    first_day_discount = 0
    client_discount_item_config = facade.find_payment_item_config('bootcamp-webdev')
    promotion_end_date = checkout_facade.launch_datetime_finish
    payment_item_config = client_discount_item_config
    client_discount = no_discount_item_config.price - client_discount_item_config.price - first_day_discount
    return _render_bootcamp_lp(
        client_discount,
        first_day_discount,
        form,
        has_client_discount,
        has_first_day_discount,
        no_discount_item_config,
        payment_item_config,
        promotion_end_date,
        request,
        'checkout/bootcamp_lp_d3.html'
    )


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


def _render_with_webdev_and_first_day_discounts(
    request, client_discount_slug, first_day_discount_slug, promotion_end_date,
    template_name='checkout/bootcamp_lp_subscription_open.html'
):
    user_domain.visit_member_landing_page(request.user, source=request.GET.get('utm_source', default='unknown'))
    has_client_discount = True
    data = {'name': request.user.first_name, 'email': request.user.email}
    form = facade.ContactForm(data)
    has_first_day_discount = True
    no_discount_item_config = facade.find_payment_item_config('bootcamp')
    first_day_discount_item_config = facade.find_payment_item_config(first_day_discount_slug)
    first_day_discount = no_discount_item_config.price - first_day_discount_item_config.price
    client_discount_item_config = facade.find_payment_item_config(client_discount_slug)
    payment_item_config = client_discount_item_config
    client_discount = no_discount_item_config.price - client_discount_item_config.price - first_day_discount
    return _render_bootcamp_lp(client_discount, first_day_discount, form, has_client_discount, has_first_day_discount,
                               no_discount_item_config, payment_item_config, promotion_end_date, request, template_name)
