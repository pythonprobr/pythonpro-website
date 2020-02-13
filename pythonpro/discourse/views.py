from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.defaults import bad_request

from pythonpro.discourse.facade import InvalidSOOPayload, generate_discourse_login_url


@login_required
def sso(request):
    """
    Proceed login into discourse

    Code based on https://meta.discourse.org/t/sso-example-for-django/14258
    """
    payload = request.GET.get('sso')
    signature = request.GET.get('sig')
    try:
        url = generate_discourse_login_url(request.user, payload, signature)
    except InvalidSOOPayload as e:
        return bad_request(request, e)
    else:
        return HttpResponseRedirect(url)
