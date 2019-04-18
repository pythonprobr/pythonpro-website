from pythonpro.promos.models import Video as _Video


def find_all_videos():
    return _Video.objects.all()
