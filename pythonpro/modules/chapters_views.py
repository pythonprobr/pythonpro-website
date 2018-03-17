from django.shortcuts import render

from pythonpro.modules import facade


def detail(request, slug):
    ctx = {'chapter': facade.get_chapter_with_contents(slug=slug)}
    return render(request, 'chapters/chapter_detail.html', context=ctx)
