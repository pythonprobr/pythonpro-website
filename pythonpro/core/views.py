from django.http import HttpResponse


def index(request):
    textomock = """
    <h1>pythonpro</h1>
    <h2>Python para Profissionais</h2>
    """
    return HttpResponse(textomock)



# from django.shortcuts import render
#
# def index(request):
#     return render(request, 'core/index.html', {})
