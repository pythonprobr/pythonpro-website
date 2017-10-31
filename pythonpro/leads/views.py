from django.core.exceptions import ValidationError
from django.forms.fields import EmailField
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView

from pythonpro.leads.models import Lead


def subscribed(request):
    return HttpResponse(b'Ok')


_create_lead_view = CreateView.as_view(
    model=Lead, fields='name email'.split(), success_url=reverse_lazy('leads:subscribed'))


def new(request):
    """Creates a new Lead if the email is not already on database"""
    email_field = EmailField()
    try:
        if Lead.objects.filter(email__exact=email_field.clean(request.POST['email'])).exists():
            return HttpResponseRedirect(reverse('leads:subscribed'))
    except ValidationError:
        pass

    return _create_lead_view(request)
