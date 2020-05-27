from inflection import underscore

from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy

from pythonpro.pages.forms import NameEmailForm
from pythonpro.email_marketing.facade import create_or_update_with_no_role


class TemplateNameMixin:
    def get_template_names(self):
        return [f"pages/{underscore(self.__class__.__name__)}.html"]


class BaseLandingPageView(TemplateNameMixin, FormView):
    form_class = NameEmailForm
    success_url = '/'

    def get_email_marketing_tag(self):
        return self.email_marketing_tag

    def form_valid(self, form):
        create_or_update_with_no_role.delay(
            form.cleaned_data['name'], form.cleaned_data['email'], self.get_email_marketing_tag()
        )
        return super().form_valid(form)


class BaseThankYouView(TemplateNameMixin, TemplateView):
    pass


class CarreiraProLandingPage(BaseLandingPageView):
    success_url = reverse_lazy('pages:carreirapro_thank_you_page')
    email_marketing_tag = 'webinario-carreira-pro'


class CarreiraProThankYouPage(BaseThankYouView):
    pass
