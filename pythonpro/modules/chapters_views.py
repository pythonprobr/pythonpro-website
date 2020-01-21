from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from pythonpro.modules import facade


@login_required
def detail_old(request, chapter_slug):
    chapter = facade.get_chapter_with_contents(slug=chapter_slug)
    return redirect(chapter.get_absolute_url(), permanent=True)


@login_required
def detail(request, module_slug, chapter_slug):
    ctx = {'chapter': facade.get_chapter_with_contents(slug=chapter_slug)}
    return render(request, 'chapters/chapter_detail.html', context=ctx)
