from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from pythonpro.modules.facade import get_module_with_contents, get_all_modules


@login_required
def detail(request, slug):
    module = get_module_with_contents(slug)
    return render(request, 'modules/module_detail.html', {'module': module})


def index(request):
    return render(request, 'modules/module_index.html', context={'modules': get_all_modules()})
