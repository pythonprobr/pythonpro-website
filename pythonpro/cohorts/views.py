from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from pythonpro.cohorts import facade
from pythonpro.memberkit import facade as memberkit_facade


@login_required
def webinars(request):
    return render(request, 'cohorts/webinars.html', {'webinars': facade.find_recorded_webinars()})


@login_required
def webinar(request, slug):
    user = request.user
    if memberkit_facade.has_memberkit_account(user):
        webinar = facade.find_webinar(slug=slug)
        return redirect(webinar.memberkit_url, permanent=True)
    if memberkit_facade.has_any_subscription(user):
        return redirect(reverse('migrate_to_memberkit'), permanent=True)
    return redirect(reverse('checkout:bootcamp_lp'), permanent=False)


@login_required
def live_class(request, pk):
    user = request.user
    if memberkit_facade.has_memberkit_account(user):
        live_class = facade.find_live_class(pk=pk)
        return redirect(live_class.memberkit_url, permanent=True)
    if memberkit_facade.has_any_subscription(user):
        return redirect(reverse('migrate_to_memberkit'), permanent=True)
    return redirect(reverse('checkout:bootcamp_lp'), permanent=False)
