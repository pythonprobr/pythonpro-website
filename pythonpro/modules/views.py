from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from pythonpro.modules.models import modules
from pythonpro.sections.facade import get_module_sections


@login_required
def detail(request, slug):
    module = modules.ALL[slug]
    module.sections = get_module_sections(module)
    ctx = dict(module=module)
    return render(request, 'modules/module_detail.html', context=ctx)


def index(request):
    return render(request, 'modules/module_index.html')
