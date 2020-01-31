from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from pythonpro.dashboard import facade as dashboard_facade
from pythonpro.dashboard.facade import has_watched_any_topic
from pythonpro.dashboard.forms import TopicInteractionForm
from pythonpro.domain import user_facade
from pythonpro.modules.models import Topic


@login_required
def home(request):
    topics = list(dashboard_facade.calculate_topic_interaction_history(request.user))

    for topic in topics:
        topic.calculated_module = topic.find_module()

    module_progresses = dashboard_facade.calculate_module_progresses(request.user)
    ctx = {'topics': topics, 'module_progresses': module_progresses}
    return render(
        request,
        'dashboard/home.html',
        ctx
    )


@login_required
@csrf_exempt
def topic_interaction(request):
    data = dict(request.POST.items())
    user = request.user
    data['user'] = user.id
    form = TopicInteractionForm(data)
    if form.is_valid():
        if not has_watched_any_topic(user):
            user_facade.activate_user(user, None)
        topic_id = int(request.POST['topic'])
        current_topic_duration = Topic.objects.values('duration').get(id=topic_id)['duration']
        maybe_new_topic_duration = form.cleaned_data['topic_duration']
        if current_topic_duration != maybe_new_topic_duration:
            Topic.objects.filter(id=topic_id).update(duration=maybe_new_topic_duration)

        return JsonResponse({'msg': 'ok'})
