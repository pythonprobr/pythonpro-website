from django.shortcuts import render

# Create your views here.
from pythonpro.redirector.models import Redirect


def redirect(request, slug: str):
    ctx = {'redirect': Redirect.objects.values('url').get(slug=slug)}
    return render(request, 'redirector/redirect.html', ctx)
