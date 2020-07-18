import os

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.static import serve

from pythonpro.absolute_uri import build_absolute_uri
from pythonpro.cohorts.facade import find_most_recent_cohort
from pythonpro.domain import user_facade
from pythonpro.email_marketing import facade as email_marketing_facade
from pythonpro.launch.facade import (
    get_launch_status,
    get_opened_cpls,
    LAUNCH_STATUS_OPEN_CART,
    LAUNCH_STATUS_PPL
)
from pythonpro.launch.forms import LeadForm


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
    return redirect(reverse('launch:cpl1'))


def ty(request):
    user = request.user
    if user.is_authenticated:
        user_facade.subscribe_launch_landing_page(user, request.GET.get('utm_source', 'unknown'))
    return render(request, 'launch/ty.html')


def cpl1(request):
    user = request.user
    visit_function = user_facade.visit_cpl1
    video_id = 'Xls9-5DnNLc'
    video_id_next_class = 'qTugLQeCn54'
    description = (
        'Nesta aula você você vai aprender como instalar o Python em seu sistema operacional, '
        'editar código e fazer pequenos testes no console.'
    )
    title = 'AULA #1: Tudo o que você precisa para começar a programar'
    return _render_cpl(
        description, request, title, user, video_id, visit_function, video_id_next_class
    )


def cpl2(request):
    user = request.user
    visit_function = user_facade.visit_cpl2
    video_id = 'qTugLQeCn54'
    video_id_next_class = 'pEj16gPFbpk'
    title = 'AULA #2: Os Fundamentos da PROGRAMAÇÃO PROCEDURAL'
    description = (
        'Nesta aula você vai aprender programação procedural. Esse paradigma consiste em'
        ' você definir a resolução de um problema, passo a passo, de forma linear. Funci'
        'ona como uma receita culinária, onde cada etapa é definida exatamente uma depoi'
        's da outra.'
    )
    return _render_cpl(
        description, request, title, user, video_id, visit_function, video_id_next_class
    )


def cpl3(request):
    user = request.user
    visit_function = user_facade.visit_cpl3
    video_id = 'pEj16gPFbpk'
    video_id_next_class = 'tTjFK4x0Qb8'
    title = 'AULA #3: Descobrindo o Mundo da ORIENTAÇÃO A OBJETO'
    description = (
        'Depois de aprender o paradigma procedural na seção anterior chega hora de conhecer '
        'outro: a Orientação a Objetos (OO). Você vai aprender sobre classes e seus componen'
        'tes, herança e utilizar esses conceitos para implementar o jogo Python Birds. Como '
        'toda mudança de paradigma, demora um tempo para se acostumar, mas é importante apre'
        'nder bem OO porque ela utilizada em inúmeras bibliotecas e frameworks.'
    )
    return _render_cpl(
        description, request, title, user, video_id, visit_function, video_id_next_class
    )


def cpl4(request):
    user = request.user
    visit_function = user_facade.visit_cpl3
    video_id = 'tTjFK4x0Qb8'
    title = 'AULA #4: A técnica Matadora para CONSEGUIR UMA VAGA + Resumão'
    description = (
        'Chegou o grande dia! Nesta aula você vai aprender uma técnica matadora para conseguir '
        'sua primeira oportunidade como Programador Profissional. Além disso, eu vou dar todas '
        'as instruções para você se matricular no Curso Python Pro, e, por fim, vou fazer um re'
        'sumão da Semana do Programador Profissional.'
    )
    return _render_cpl(description, request, title, user, video_id, visit_function, video_id)


def _render_cpl(description, request, title, user, video_id, visit_function, video_id_next_class=None):
    if user.is_authenticated:
        visit_function(user, request.GET.get('utm_source', 'unknown'))

    launch_status = get_launch_status()
    if launch_status == LAUNCH_STATUS_PPL and not request.GET.get('debug'):
        return redirect(reverse('launch:landing_page'))

    if launch_status == LAUNCH_STATUS_OPEN_CART and not request.GET.get('debug'):
        return redirect(reverse('checkout:membership_lp'))

    ctx = {
        'data_href': f'https://{build_absolute_uri(request.path)}',
        'video_id': video_id,
        'video_id_next_class': video_id_next_class,
        'title': title,
        'description': description,
        'launch_status': launch_status,
        'opened_cpls': get_opened_cpls(),
        'DEBUG': settings.DEBUG,
    }
    return render(request, 'launch/cpl.html', ctx)


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


def _render_launch_page(is_launch_open, request, template_closed_launch, template_open_launch, redirect_path_name: str):
    user = request.user
    if user.is_authenticated:
        user_facade.visit_member_landing_page(request.user, source=request.GET.get('utm_source', default='unknown'))
    template = template_closed_launch
    return render(request, template, {})
