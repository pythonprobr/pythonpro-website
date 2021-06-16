from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from pythonpro.memberkit import facade


@login_required
def login_on_memberkit(request):
    return redirect(facade.create_login_url(request.user))
