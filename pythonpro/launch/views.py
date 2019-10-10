from django.shortcuts import redirect, render
# Create your views here.
from django.urls import reverse

from pythonpro.cohorts.facade import find_most_recent_cohort
from pythonpro.domain import user_facade
from pythonpro.launch.forms import LeadForm
from pythonpro.mailchimp import facade as mailchimp_facade


def landing_page(request):
    user = request.user
    if user.is_authenticated:
        form = LeadForm({'email': user.email})
        user_facade.visit_launch_landing_page(user, request.GET.get('utm_source', 'unknown'))
    else:
        form = LeadForm()
    return render(request, 'launch/landing_page.html', {'form': form})


def lead_form(request):
    form = LeadForm(request.POST)
    if not form.is_valid():
        return render(request, 'launch/form.html', {'form': form}, status=400)
    email = form.cleaned_data['email']
    user = request.user
    if user.is_authenticated:
        first_name = user.first_name
    else:
        first_name = email.split('@')[0]
    mailchimp_facade.create_or_update_with_no_role(
        first_name,
        email,
        f'turma-{find_most_recent_cohort().slug}-semana-do-programador')
    return redirect(reverse('launch:ty'))


def ty(request):
    user = request.user
    cohort_slug = find_most_recent_cohort().slug
    python_birds_path = reverse('core:lead_landing') + f'?utm_source=lancamento-{cohort_slug}'
    if user.is_authenticated:
        user_facade.subscribe_launch_landing_page(user, request.GET.get('utm_source', 'unknown'))
    return render(request, 'launch/ty.html', {'python_birds_path': python_birds_path})
