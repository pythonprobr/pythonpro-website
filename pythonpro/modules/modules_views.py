from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from pythonpro.modules import models
from pythonpro.modules.facade import get_module_sections, get_all_modules


@login_required
def detail(request, slug):
    module = models.ALL[slug]
    module.sections = get_module_sections(module)
    ctx = dict(module=module)
    return render(request, 'modules/module_detail.html', context=ctx)


def index(request):
    return render(request, 'modules/module_index.html', context={'modules': get_all_modules()})
