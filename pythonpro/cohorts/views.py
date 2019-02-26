from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pythonpro.cohorts import facade


@login_required
def detail(request, slug):
    return render(request, 'cohorts/cohort_detail.html', {'cohort': facade.find_cohort(slug=slug)})


@login_required
def webinars(request):
    return render(request, 'cohorts/webinars.html', {'webinars': facade.find_webinars()})


@login_required
def webinar(request, slug):
    return render(request, 'cohorts/webinar_detail.html', {'webinar': facade.find_webinar(slug=slug)})
