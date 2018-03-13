from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from pythonpro.modules.models import modules


@login_required
def module(request, slug):
    ctx = dict(module=modules.ALL[slug])
    return render(request, 'modules/module_detail.html', context=ctx)


def index(request):
    return render(request, 'modules/module_index.html')
