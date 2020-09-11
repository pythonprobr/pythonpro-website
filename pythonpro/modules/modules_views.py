from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rolepermissions.checkers import has_object_permission

from pythonpro.domain.content_statistics_domain import calculate_module_progresses_using_slug
from pythonpro.email_marketing.facade import tag_as
from pythonpro.modules.facade import get_all_modules, get_module_with_contents, add_modules_purchase_link


@login_required
def detail(request, slug):
    module = calculate_module_progresses_using_slug(request.user, slug)
    return render(request, 'modules/module_detail.html', context={'module': module})


def index(request):
    modules = get_all_modules()
    modules = add_modules_purchase_link(modules)

    for module in modules:
        module.has_access = True if has_object_permission('access_content', request.user, module) else False

    return render(request, 'modules/module_index.html', context={'modules': modules})


@login_required
def enrol(request, slug):
    module = get_module_with_contents(slug)
    user = request.user
    tag_as(user.email, user.id, slug)
    return render(request, 'modules/module_enrol.html', context={'module': module})


def description(request, slug):
    module = get_module_with_contents(slug)
    return render(request, 'modules/module_description.html', context={'module': module})
