from django.shortcuts import render

from pythonpro.redirector.models import Redirect
from pythonpro.redirector.facade import get_redirect_url


def redirect(request, slug: str):
    redirect = Redirect.objects.get(slug=slug)
    ctx = {'url': get_redirect_url(redirect)}
    return render(request, 'redirector/redirect.html', ctx)
