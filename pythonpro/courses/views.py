from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from pythonpro.courses.models import courses


@login_required
def course(request, slug):
    ctx = dict(course=courses.ALL[slug])
    return render(request, 'courses/course_detail.html', context=ctx)


def index(request):
    return render(request, 'courses/course_index.html')
