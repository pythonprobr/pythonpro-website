from django.shortcuts import render


# Create your views here.

def video(request, slug):
    return render(request, 'promos/video_detail.html', {})
