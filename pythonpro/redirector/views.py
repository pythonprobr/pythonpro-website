from django.shortcuts import render, redirect as redirect_url

from pythonpro.redirector.models import Redirect
from pythonpro.redirector.facade import get_redirect_url


def redirect(request, slug: str):
    redirect = Redirect.objects.get(slug=slug)
    url = get_redirect_url(redirect)

    if redirect.use_javascript is False:
        url = f'{url}?{request.GET.urlencode()}'
        return redirect_url(url)

    ctx = {'url': url}
    return render(request, 'redirector/redirect.html', ctx)
