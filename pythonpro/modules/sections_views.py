from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from pythonpro.modules import facade


@login_required
def detail_old(request, slug):
    section = facade.get_section_with_contents(slug=slug)
    return redirect(section.get_absolute_url(), permanent=True)


@login_required
def detail(request, module_slug, section_slug):
    ctx = {'section': facade.get_section_with_contents(slug=section_slug)}
    return render(request, 'sections/section_detail.html', ctx)
