from django.shortcuts import render


# Create your views here.

def video(request, slug):
    return render(request, 'promos/video_detail.html', {})


def thanks(request):
    return render(request, 'promos/subscriptions_thanks.html', {})
