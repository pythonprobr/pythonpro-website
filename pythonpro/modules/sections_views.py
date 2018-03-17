from django.shortcuts import render

from pythonpro.modules import facade


def detail(request, slug):
    ctx = {'section': facade.get_section_with_module_and_chapters(slug=slug)}
    return render(request, 'sections/section_detail.html', ctx)
