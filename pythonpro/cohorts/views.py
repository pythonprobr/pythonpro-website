from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pythonpro.cohorts import facade


@login_required
def detail(request, slug):
    return render(request, 'cohorts/cohort_detail.html', {'cohort': facade.find_cohort(slug=slug)})
