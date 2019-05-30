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
from rolepermissions.roles import assign_role, remove_role

from pythonpro.mailchimp import facade as mailchimp_facade
from pythonpro.payments import facade as payment_facade
from pythonpro.payments.facade import PYTOOLS_PRICE


def options(request):
    template = 'payments/options_detail.html' if settings.SUBSCRIPTIONS_OPEN else 'payments/closed_subscriptions.html'
    return render(request, template, {})


def thanks(request):
    return render(request, 'payments/thanks.html')


@login_required
@csrf_exempt
def pytools_capture(request):
    if request.method != 'POST':
        return
    pagarme_resp = payment_facade.pytools_capture(request.POST['token'])
    if pagarme_resp['payment_method'] == 'credit_card':
        user = request.user
        _promote_client(user)
        dct = {'redirect_url': reverse('payments:pytools_thanks')}
    elif pagarme_resp['payment_method'] == 'boleto':
        path = reverse('payments:pytools_boleto')
        qs = urlencode(_extract_boleto_params(pagarme_resp))
        dct = {'redirect_url': f'{path}?{qs}'}
    return JsonResponse(dct)


def _promote_client(user):
    remove_role(user, 'lead')
    assign_role(user, 'client')
    mailchimp_facade.create_or_update_client(user.first_name, user.email)


def pytools_thanks(request):
    return render(request, 'payments/pytools_thanks.html')


def pytools_boleto(request):
    dct = request.GET
    context = _extract_boleto_params(dct)
    return render(request, 'payments/pytools_boleto.html', context=context)


def _extract_boleto_params(dct):
    return {k: dct[k] for k in ['boleto_barcode', 'boleto_url']}


@login_required
def client_landing_page(request):
    notification_url = reverse('payments:pagarme_notification', kwargs={'user_id': request.user.id})
    return render(
        request,
        'payments/client_landing_page.html', {
            'PAGARME_CRYPTO_KEY': settings.PAGARME_CRYPTO_KEY,
            'price': PYTOOLS_PRICE,
            'notification_url': request.build_absolute_uri(
                notification_url
            )
        })


def pagarme_notification(request, user_id: int):
    if request.method != 'POST':
        return HttpResponseNotAllowed([request.method])

    paymento_ok = payment_facade.confirm_boleto_payment(
        user_id, request.POST, request.body.decode('utf8'), request.headers['X-Hub-Signature'])
    if paymento_ok:
        user = get_user_model().objects.get(id=user_id)
        _promote_client(user)
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
    return HttpResponse('')
