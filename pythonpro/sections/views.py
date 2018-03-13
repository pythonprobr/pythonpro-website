from django.shortcuts import render, get_object_or_404

from pythonpro.sections.models import Section


def detail(request, slug):
    ctx = {'section': get_object_or_404(Section, slug=slug)}
    return render(request, 'sections/section_detail.html', ctx)
