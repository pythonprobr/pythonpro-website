from django.shortcuts import render


def index(request):
    return render(request, 'core/index.html', {})


def thanks(request):
    return render(request, 'core/lead_thanks.html', {})
