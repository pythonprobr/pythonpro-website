from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pythonpro.modules import facade


@login_required
def detail(request, slug):
    ctx = {'chapter': facade.get_chapter_with_contents(slug=slug)}
    return render(request, 'chapters/chapter_detail.html', context=ctx)
