from django.shortcuts import render

# Create your views here.
from pythonpro.promos.models import Video


def video(request, slug):
    video = Video.objects.filter(slug__exact=slug).get()
    return render(request, 'promos/video_detail.html', {'video': video})


def thanks(request):
    return render(request, 'promos/subscriptions_thanks.html', {})
