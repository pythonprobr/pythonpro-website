from django.shortcuts import redirect
# Create your views here.
from django.urls import reverse


def video(request, slug):
    return redirect(reverse('core:lead_landing'), permanent=True)
