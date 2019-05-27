from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rolepermissions.roles import assign_role, remove_role

from pythonpro.mailchimp import facade as mailchimp_facade
from pythonpro.payments import facade as payment_facade


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
    payment_facade.pytools_capture(request.POST['token'])
    user = request.user
    remove_role(user, 'lead')
    assign_role(user, 'client')
    mailchimp_facade.create_or_update_client(user.first_name, user.email)
    return JsonResponse({'redirect_url': reverse('payments:pytools_thanks')})


def pytools_thanks(request):
    return render(request, 'payments/pytools_thanks.html')
