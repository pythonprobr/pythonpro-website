from django.conf import settings
from django.shortcuts import render


def options(request):
    template = 'payments/options_detail.html' if settings.SUBSCRIPTIONS_OPEN else 'payments/closed_subscriptions.html'
    return render(request, template, {})


def thanks(request):
    return render(request, 'payments/thanks.html')
