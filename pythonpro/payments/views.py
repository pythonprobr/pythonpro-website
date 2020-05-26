from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from pythonpro.cohorts import facade as cohorts_facade
from pythonpro.core.facade import UserRoleException
from pythonpro.domain import membership_domain, user_facade
from pythonpro.payments import facade as payment_facade
from pythonpro.payments.facade import PagarmeNotPaidTransaction


def thanks(request):
    return render(request, 'payments/thanks.html')


def membership_thanks(request):
    return render(request, 'payments/membership_thanks.html', {'cohort': cohorts_facade.find_most_recent_cohort()})


@csrf_exempt
def member_capture(request):
    if request.method != 'POST':
        return
    user = request.user
    token = request.POST['token']
    dct = membership_domain.capture_payment(token, user, request.GET.get('utm_source', default='unknown'))
    return JsonResponse(dct)


@login_required
@csrf_exempt
def member_checkout(request):
    """
   Track user who clicked on client LP Checkout button
   :param request:
   :return:
   """
    if request.method != 'POST':
        return
    user_facade.click_member_checkout(request.user)
    return JsonResponse({'client-checkout': 'ok'})


def _promote_client(user, request):
    user_facade.promote_client(user, source=request.GET.get('utm_source', default='unknown'))


def _promote_client_and_remove_tag_boleto(user, request):
    try:
        user_facade.promote_client_and_remove_boleto_tag(user, source=request.GET.get('utm_source', default='unknown'))
    except UserRoleException:
        pass  # No need to handle since user can be a client due to active marketing


def membership_boleto(request):
    dct = request.GET
    context = _extract_boleto_params(dct)
    return render(request, 'payments/membership_boleto.html', context=context)


def _extract_boleto_params(dct):
    return {k: dct[k] for k in ['boleto_barcode', 'boleto_url']}


def member_landing_page(request):
    template_open_launch = 'payments/meteoric_landing_page_open.html'
    template_closed_launch = 'payments/member_landing_page_subscription_closed.html'
    is_launch_open = settings.SUBSCRIPTIONS_OPEN or request.GET.get('debug')
    return _render_launch_page(is_launch_open, request, template_closed_launch, template_open_launch,
                               'member_landing_page')


old_member_landing_page = RedirectView.as_view(pattern_name='member_landing_page', permanent=True)


def meteoric_landing_page(request):
    template_open_launch = 'payments/meteoric_landing_page_open.html'
    template_closed_launch = 'payments/meteoric_landing_page_closed.html'
    is_launch_open = settings.METEORIC_LAUNCH_OPEN or request.GET.get('debug')
    return _render_launch_page(is_launch_open, request, template_closed_launch, template_open_launch,
                               'meteoric_landing_page')


def _render_launch_page(is_launch_open, request, template_closed_launch, template_open_launch, redirect_path_name: str):
    user = request.user
    if user.is_authenticated:
        user_facade.visit_member_landing_page(request.user, source=request.GET.get('utm_source', default='unknown'))
        notification_url = reverse('payments:membership_notification', kwargs={'user_id': user.id})
    else:
        notification_url = reverse('payments:membership_anonymous_notification')
    if is_launch_open:
        template = template_open_launch
        discount = membership_domain.calculate_discount(user)
        discount_float = discount / 100

        price = membership_domain.calculate_membership_price(user)
        price_float = price / 100
        full_price_float = price_float + discount_float
        price_installment = (price // 10) / 100
        full_price_installment = full_price_float // 10
        login_url = reverse('login')
        redirect_path = reverse(redirect_path_name)
        qs = urlencode({'utm_source': request.GET.get('utm_source', 'unknown')})
        redirect_url = f'{redirect_path}?{qs}'
        qs = urlencode({'next': redirect_url})
        login_url = f'{login_url}?{qs}'
        return render(
            request,
            template,
            {
                'PAGARME_CRYPTO_KEY': settings.PAGARME_CRYPTO_KEY,
                'price': price,
                'price_float': price_float,
                'price_installment': price_installment,
                'notification_url': request.build_absolute_uri(notification_url),
                'cohort': cohorts_facade.find_most_recent_cohort(),
                'has_discount': discount_float > 0,
                'discount_float': discount_float,
                'full_price_installment': full_price_installment,
                'full_price_float': full_price_float,
                'login_url': login_url,
            }
        )
    else:
        template = template_closed_launch
        return render(request, template, {})


@csrf_exempt
def membership_notification(request, user_id: int):
    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])
    membership_domain.subscribe_member_who_paid_boleto(
        user_id,
        request.POST,
        request.body.decode('utf8'),
        request.headers['X-Hub-Signature'],
        request.GET.get('utm_source', default='unknown')
    )
    return HttpResponse('')


@csrf_exempt
def pagarme_notification(request, user_id: int):
    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])
    try:
        payment_facade.confirm_boleto_payment(
            user_id, request.POST, request.body.decode('utf8'), request.headers['X-Hub-Signature'])
    except PagarmeNotPaidTransaction:
        pass
    else:
        user = user_facade.find_user_by_id(user_id)
        _promote_client_and_remove_tag_boleto(user, request)
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
        user = user_facade.find_user_by_email(transaction['customer']['email'])
        _promote_client_and_remove_tag_boleto(user, request)
    return HttpResponse('')


@csrf_exempt
def membership_anonymous_notification(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])
    membership_domain.subscribe_anonymous_member_who_paid_boleto(
        request.POST,
        request.body.decode('utf8'),
        request.headers['X-Hub-Signature'],
        request.GET.get('utm_source', default='unknown')
    )

    return HttpResponse('')
