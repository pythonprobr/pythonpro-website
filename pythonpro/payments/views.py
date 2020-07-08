from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from pythonpro.cohorts import facade as cohorts_facade
from pythonpro.core.facade import UserRoleException
from pythonpro.domain import membership_domain, user_facade


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


old_member_landing_page = RedirectView.as_view(pattern_name='member_landing_page', permanent=True)


