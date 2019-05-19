from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pythonpro.modules.facade import get_all_modules, get_module_with_contents


@login_required
def detail(request, slug):
    module = get_module_with_contents(slug)
    return render(request, 'modules/module_detail.html', {'module': module})


def index(request):
    return render(request, 'modules/module_index.html', context={'modules': get_all_modules()})
