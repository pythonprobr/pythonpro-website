from datetime import timedelta
from inflection import underscore

from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.utils import timezone

from pythonpro.cohorts.facade import find_most_recent_cohort
from pythonpro.pages.forms import NameEmailForm, NameEmailPhoneForm
from pythonpro.domain.subscription_domain import subscribe_with_no_role


class TemplateNameMixin:
    def get_template_names(self):
        return [f"pages/{underscore(self.__class__.__name__)}.html"]


class BaseLandingPageView(TemplateNameMixin, FormView):
    form_class = NameEmailForm
    success_url = '/'

    def get_email_marketing_tag(self):
        return self.email_marketing_tag

    def form_valid(self, form):
        args = [form.cleaned_data['name'], form.cleaned_data['email'], self.get_email_marketing_tag()]
        kwargs = {}

        if form.cleaned_data.get('phone') is not None:
            if self.request.user.is_authenticated is True:
                kwargs['id'] = self.request.user.id
            kwargs['phone'] = f"+55{form.cleaned_data['phone']}"

        session_id = self.request.session.session_key
        subscribe_with_no_role.delay(session_id, *args, **kwargs)
        return super().form_valid(form)


class BaseThankYouView(TemplateNameMixin, TemplateView):
    pass


class BasePhoneLandingPageView(BaseLandingPageView):
    form_class = NameEmailPhoneForm

    def get_initial(self):
        is_name_or_email_setted = self.request.GET.get('name') is not None or self.request.GET.get('email') is not None
        if is_name_or_email_setted is True:
            return self.request.GET

        if self.request.user.is_authenticated is True:
            return {
                'name': self.request.user.first_name,
                'email': self.request.user.email,
            }

        return super().get_initial()


class CarreiraProLandingPage(BaseLandingPageView):
    success_url = reverse_lazy('pages:carreirapro_thank_you_page')
    email_marketing_tag = 'webinario-carreira-pro'


class CarreiraProThankYouPage(BaseThankYouView):
    pass


class DsWebinarLandingPage(BaseLandingPageView):
    success_url = reverse_lazy('pages:ds_webinar_thank_you_page')
    email_marketing_tag = 'webinario-data-science'


class DsWebinarThankYouPage(BaseThankYouView):
    pass


class LeadsOnboardingPage(BaseThankYouView):
    pass


class BootcampVipLandingPage(BasePhoneLandingPageView):
    success_url = reverse_lazy('pages:bootcamp_vip_thank_you_page')

    def get_email_marketing_tag(self):
        return f'turma-{find_most_recent_cohort().slug}-semana-do-programador-grupo-vip'


class BootcampVipThankYouPage(BaseThankYouView):
    pass


class TppWebioricoLandingPage(BaseLandingPageView):
    success_url = reverse_lazy('pages:tpp_webiorico_thank_you_page')
    email_marketing_tag = 'tpp-webiorico'

    def get_next_wed(self):
        if self.kwargs.get('date') is not None:
            return self.kwargs.get('date').replace('-', '/')

        now = timezone.now()
        days_ahead = 2 - now.weekday()

        if days_ahead - 2 <= 0:
            days_ahead += 7

        final_date = now + timedelta(days=days_ahead)
        return final_date.strftime("%d/%m")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['date'] = self.get_next_wed()
        return context


class TppWebioricoThankYouPage(BaseThankYouView):
    pass
