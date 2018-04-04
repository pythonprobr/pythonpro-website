from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pythonpro.modules import facade


@login_required
def detail(request, slug):
    ctx = {'topic': facade.get_topic_with_contents(slug=slug)}
    return render(request, 'topics/topic_detail.html', context=ctx)
