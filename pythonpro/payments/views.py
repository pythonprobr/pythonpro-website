from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from pythonpro import facade
from pythonpro.mailchimp.facade import tag_as
from pythonpro.payments import facade as payment_facade
from pythonpro.payments.facade import PYTOOLS_PRICE, PYTOOLS_PROMOTION_PRICE, PagarmeNotPaidTransaction


def options(request):
    template = 'payments/options_detail.html' if settings.SUBSCRIPTIONS_OPEN else 'payments/closed_subscriptions.html'
    return render(request, template, {})


def thanks(request):
    return render(request, 'payments/thanks.html')


@csrf_exempt
def pytools_capture(request):
    if request.method != 'POST':
        return
    user = request.user
    user_creation = user.date_joined if user.is_authenticated else now()
    pagarme_resp = payment_facade.pytools_capture(request.POST['token'], user_creation)
    customer = pagarme_resp['customer']
    customer_email = customer['email']
    source = request.GET.get('utm_source', default='unknown')
    customer_first_name = customer['name'].split()[0]
    payment_method = pagarme_resp['payment_method']
    if payment_method == 'credit_card':
        if user.is_authenticated:
            _promote_client(user, request)
        else:
            facade.force_register_client(customer_first_name, customer_email, source)
        dct = {'redirect_url': reverse('payments:pytools_thanks')}
    elif payment_method == 'boleto':
        if not user.is_authenticated:
            facade.force_register_lead(customer_first_name, customer_email, source)
        path = reverse('payments:pytools_boleto')
        qs = urlencode(_extract_boleto_params(pagarme_resp))
        dct = {'redirect_url': f'{path}?{qs}'}
    else:
        raise ValueError(f'Invalid payment method {payment_method}')
    return JsonResponse(dct)


@login_required
@csrf_exempt
def client_checkout(request):
    """
    Track user who clicked on client LP Checkout button
    :param request:
    :return:
    """
    if request.method != 'POST':
        return
    tag_as(request.user.email, 'client-checkout')
    return JsonResponse({'client-checkout': 'ok'})


def _promote_client(user, request):
    msg = render_to_string(
        'payments/pytools_email.txt',
        {
            'user': user,
            'ty_url': request.build_absolute_uri(reverse('payments:pytools_thanks'))
        }
    )
    facade.promote_client(user, msg)


def pytools_thanks(request):
    return render(request, 'payments/pytools_thanks.html')


def pytools_boleto(request):
    dct = request.GET
    context = _extract_boleto_params(dct)
    return render(request, 'payments/pytools_boleto.html', context=context)


def _extract_boleto_params(dct):
    return {k: dct[k] for k in ['boleto_barcode', 'boleto_url']}


def client_landing_page(request):
    user = request.user
    if user.is_authenticated:
        tag_as(user.email, 'potential-client')
        notification_url = reverse('payments:pagarme_notification', kwargs={'user_id': user.id})
    else:
        notification_url = reverse('payments:pagarme_anonymous_notification')
    user_creation = user.date_joined if user.is_authenticated else now()
    is_promotion_season = payment_facade.is_on_pytools_promotion_season(user_creation)
    price = PYTOOLS_PROMOTION_PRICE if is_promotion_season else PYTOOLS_PRICE
    price_float = price / 100
    _, promotion_end_date = payment_facade.calculate_pytools_promotion_interval()
    return render(
        request,
        'payments/client_landing_page.html', {
            'PAGARME_CRYPTO_KEY': settings.PAGARME_CRYPTO_KEY,
            'price': price,
            'price_float': price_float,
            'is_promotion_season': is_promotion_season,
            'promotion_end_date': promotion_end_date,
            'notification_url': request.build_absolute_uri(
                notification_url
            )
        })


@login_required
def member_landing_page(request):
    tag_as(request.user.email, 'potential-member')
    return render(
        request, 'payments/member_landing_page.html', {})


@login_required
def waiting_list_ty(request):
    tag_as(request.user.email, 'lista-de-espera')
    return render(request, 'payments/waiting_list_ty.html', {'email': request.user.email})


@csrf_exempt
def pagarme_notification(request, user_id: int):
    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])
    try:
        payment_facade.confirm_boleto_payment(
            user_id, request.POST, request.body.decode('utf8'), request.headers['X-Hub-Signature'])
    except PagarmeNotPaidTransaction:
        pass  # No problem, we need to handle only paid transactions
    else:
        user = facade.find_user_by_id(user_id)
        _promote_client(user, request)
    return HttpResponse('')


@csrf_exempt
def pagarme_anonymous_notification(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])
    try:
        transaction = payment_facade.extract_transaction(
            request.POST, request.body.decode('utf8'), request.headers['X-Hub-Signature'])
    except PagarmeNotPaidTransaction:
        pass  # No problem, we need to handle only paid transactions
    else:
        user = facade.find_user_by_email(transaction['customer']['email'])
        _promote_client(user, request)
    return HttpResponse('')
