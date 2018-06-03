from django.shortcuts import render

# Create your views here.
from pythonpro.cohorts.models import Cohort


def detail(request, slug):
    return render(request, 'cohorts/cohort_detail.html', {'cohort': Cohort.objects.get(slug=slug)})
