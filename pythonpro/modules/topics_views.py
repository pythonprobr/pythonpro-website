from django.shortcuts import render

from pythonpro.modules import facade


def detail(request, slug):
    ctx = {'topic': facade.get_topic_with_contents(slug=slug)}
    return render(request, 'topics/topic_detail.html', context=ctx)
