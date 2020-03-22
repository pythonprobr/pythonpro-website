import os
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from django.shortcuts import redirect, render
from django.views.static import serve
from django.urls import reverse

from pythonpro.absolute_uri import build_absolute_uri
from pythonpro.cohorts.facade import find_most_recent_cohort
from pythonpro.domain import user_facade
from pythonpro.launch.forms import LeadForm
from pythonpro.email_marketing import facade as email_marketing_facade

LAUNCH_STATUS_PPL = 0
LAUNCH_STATUS_CPL1 = 1
LAUNCH_STATUS_CPL2 = 2
LAUNCH_STATUS_CPL3 = 3
LAUNCH_STATUS_OPEN_CART = 4


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
    first_name = form.cleaned_data['name']
    user = request.user
    if user.is_authenticated:
        email_marketing_facade.create_or_update_with_no_role(
            first_name,
            email,
            f'turma-{find_most_recent_cohort().slug}-semana-do-programador', id=user.id)
    else:
        email_marketing_facade.create_or_update_with_no_role(
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
    video_id = 'oPsK7uEq-gU'
    description = 'Primeira Aula da Semana do Programador Profissional'
    return _render_cpl(description, request, 'Primeira Aula', user, video_id, visit_function)


def cpl2(request):
    user = request.user
    visit_function = user_facade.visit_cpl2
    video_id = 'wQG1dQgw78Q'
    description = 'Segunda Aula da Semana do Programador Profissional'
    return _render_cpl(description, request, 'Segunda Aula', user, video_id, visit_function)


def cpl3(request):
    user = request.user
    visit_function = user_facade.visit_cpl3
    video_id = 'v8boGknyB1E'
    description = 'Terceira Aula da Semana do Programador Profissional'
    return _render_cpl(description, request, 'Terceira Aula', user, video_id, visit_function)


def _render_cpl(description, request, title, user, video_id, visit_function):
    if user.is_authenticated:
        visit_function(user, request.GET.get('utm_source', 'unknown'))

    launch_status = _get_launch_status()
    if launch_status == LAUNCH_STATUS_PPL and not request.GET.get('debug'):
        return redirect(reverse('launch:landing_page'))

    if launch_status > LAUNCH_STATUS_CPL3 and not request.GET.get('debug'):
        return redirect(reverse('member_landing_page'))

    ctx = {
        'data_href': f'https://{build_absolute_uri(request.path)}',
        'video_id': video_id,
        'title': title,
        'description': description,
        'launch_status': launch_status,
    }
    return render(request, 'launch/cpl.html', ctx)


def _get_launch_status():
    if timezone.now() < timezone.make_aware(datetime(2019, 10, 28)):
        return LAUNCH_STATUS_PPL

    if timezone.now() < timezone.make_aware(datetime(2019, 10, 30)):
        return LAUNCH_STATUS_CPL1

    if timezone.now() < timezone.make_aware(datetime(2019, 11, 1)):
        return LAUNCH_STATUS_CPL2

    if timezone.now() < timezone.make_aware(datetime(2019, 11, 4)):
        return LAUNCH_STATUS_CPL3

    return LAUNCH_STATUS_OPEN_CART


def onesignal_sdk_worker(request):
    return serve(
        request,
        'js/spp/OneSignalSDKWorker.js',
        document_root=os.path.join(settings.BASE_DIR, 'pythonpro', 'core', 'static')
    )


def onesignal_sdk_updater_worker(request):
    return serve(
        request,
        'js/spp/OneSignalSDUpdaterKWorker.js',
        document_root=os.path.join(settings.BASE_DIR, 'pythonpro', 'core', 'static')
    )
