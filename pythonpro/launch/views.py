from django.shortcuts import redirect, render
# Create your views here.
from django.urls import reverse

from pythonpro.absolute_uri import build_absolute_uri
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
    if user.is_authenticated:
        user_facade.subscribe_launch_landing_page(user, request.GET.get('utm_source', 'unknown'))
    return render(request, 'launch/ty.html')


def cpl1(request):
    user = request.user
    visit_function = user_facade.visit_cpl1
    video_id = ''
    description = 'Primeira Aula da Semana do Programador Profissional'
    return _render_cpl(description, request, 'Primeira Aula', user, video_id, visit_function)


def cpl2(request):
    user = request.user
    visit_function = user_facade.visit_cpl2
    video_id = ''
    description = 'Segunda Aula da Semana do Programador Profissional'
    return _render_cpl(description, request, 'Segunda Aula', user, video_id, visit_function)


def cpl3(request):
    user = request.user
    visit_function = user_facade.visit_cpl3
    video_id = ''
    description = 'Terceira Aula da Semana do Programador Profissional'
    return _render_cpl(description, request, 'Terceira Aula', user, video_id, visit_function)


def _render_cpl(description, request, title, user, video_id, visit_function):
    if user.is_authenticated:
        visit_function(user, request.GET.get('utm_source', 'unknown'))
    ctx = {
        'data_href': f'https://{build_absolute_uri(request.path)}',
        'video_id': video_id,
        'title': title,
        'description': description,
    }
    return render(request, 'launch/cpl.html', ctx)
