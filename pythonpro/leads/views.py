from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView

from pythonpro.leads.models import Lead


def subscribed(request):
    return HttpResponse(b'Ok')


class LeadCreateView(CreateView):
    model = Lead
    fields = 'name email'.split()
    success_url = reverse_lazy('leads:subscribed')

    def form_invalid(self, form):
        if len(form.errors) == 1 and form.has_error('email', 'unique'):
            return HttpResponseRedirect(self.success_url)
        return super().form_invalid(form)


new = LeadCreateView.as_view()
