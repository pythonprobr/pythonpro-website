from django.http.response import HttpResponse


# Create your views here.
def new(request):
    return HttpResponse(b'Foo')
