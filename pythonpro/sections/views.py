from django.shortcuts import render


def detail(request, slug):
    return render(request, 'sections/section_detail.html')
