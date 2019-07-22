from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from mailchimp3.mailchimpclient import MailChimpError
from rolepermissions.roles import assign_role, remove_role

from pythonpro.core.forms import UserSignupForm
from pythonpro.mailchimp import facade as mailchimp_facade
from pythonpro.mailchimp.facade import tag_as
from pythonpro.payments import facade as payment_facade
from pythonpro.payments.facade import PYTOOLS_PRICE, PagarmeNotPaidTransaction


def options(request):
    template = 'payments/options_detail.html' if settings.SUBSCRIPTIONS_OPEN else 'payments/closed_subscriptions.html'
    return render(request, template, {})


def thanks(request):
    return render(request, 'payments/thanks.html')


@csrf_exempt
def pytools_capture(request):
    if request.method != 'POST':
        return
    pagarme_resp = payment_facade.pytools_capture(request.POST['token'])
    user = request.user
    if not user.is_authenticated:
        customer = pagarme_resp['customer']
        customer_email = customer['email']
        if not get_user_model().objects.filter(email=customer_email).exists():
            customer_first_name = customer['name'].split()[0]
            form = UserSignupForm({'first_name': customer_first_name, 'email': customer_email})
            source = request.GET.get('utm_source', default='unknown')
            user = form.save(source=source)
            if not pagarme_resp['payment_method'] == 'credit_card':
                assign_role(user, 'lead')
                try:
                    mailchimp_facade.create_or_update_lead(customer_first_name, customer_email)
                except MailChimpError:
                    pass

    if pagarme_resp['payment_method'] == 'credit_card':
        _promote_client(user, request)
        dct = {'redirect_url': reverse('payments:pytools_thanks')}
    elif pagarme_resp['payment_method'] == 'boleto':
        path = reverse('payments:pytools_boleto')
        qs = urlencode(_extract_boleto_params(pagarme_resp))
        dct = {'redirect_url': f'{path}?{qs}'}
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
    remove_role(user, 'lead')
    assign_role(user, 'client')
    try:
        mailchimp_facade.create_or_update_client(user.first_name, user.email)
    except MailChimpError:
        pass
    msg = render_to_string(
        'payments/pytools_email.txt',
        {
            'user': user,
            'ty_url': request.build_absolute_uri(reverse('payments:pytools_thanks'))
        }
    )
    send_mail(
        'Inscrição no curso Pytool realizada! Confira o link com detalhes.',
        msg,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )


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
    return render(
        request,
        'payments/client_landing_page.html', {
            'PAGARME_CRYPTO_KEY': settings.PAGARME_CRYPTO_KEY,
            'price': PYTOOLS_PRICE,
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
        user = get_user_model().objects.get(id=user_id)
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
        user = get_user_model().objects.filter(email=transaction['customer']['email']).get()
        _promote_client(user, request)
    return HttpResponse('')
