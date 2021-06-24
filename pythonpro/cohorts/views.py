from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from rolepermissions.checkers import has_permission

from pythonpro.cohorts import facade
from pythonpro.core.roles import access_cohorts
from pythonpro.memberkit import facade as memberkit_facade


@login_required
def detail(request, slug):
    return render(request, 'cohorts/cohort_detail.html', {'cohort': facade.find_cohort(slug=slug)})


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
    if not has_permission(request.user, access_cohorts):
        return redirect(reverse('checkout:bootcamp_lp'), permanent=False)
    return render(request, 'cohorts/live_class_detail.html', {'live_class': facade.find_live_class(pk=pk)})
