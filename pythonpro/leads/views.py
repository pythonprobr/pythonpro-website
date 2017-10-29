from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from pythonpro.leads.models import Lead


def subscribed(request):
    return HttpResponse(b'Ok')


new = CreateView.as_view(model=Lead, fields='name email'.split(), success_url=reverse_lazy('leads:subscribed'))
