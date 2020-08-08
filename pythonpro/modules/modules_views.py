from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pythonpro.email_marketing.facade import tag_as
from pythonpro.modules.facade import get_all_modules, get_module_with_contents


@login_required
def detail(request, slug):
    module = get_module_with_contents(slug)
    return render(request, 'modules/module_detail.html', context={'module': module})


def index(request):
    return render(request, 'modules/module_index.html', context={'modules': get_all_modules()})


@login_required
def enrol(request, slug):
    module = get_module_with_contents(slug)
    user = request.user
    tag_as(user.email, user.id, slug)
    return render(request, 'modules/module_enrol.html', context={'module': module})


def description(request, slug):
    module = get_module_with_contents(slug)
    return render(request, 'modules/module_description.html', context={'module': module})
