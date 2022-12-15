from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from pythonpro.dashboard.facade import has_watched_any_topic
from pythonpro.dashboard.forms import TopicInteractionForm
from pythonpro.domain import content_statistics_domain, user_domain
from pythonpro.memberkit.models import Subscription
from pythonpro.modules.models import Topic


@login_required
def certificate(request, module_slug):
    module_progresses = content_statistics_domain.calculate_modules_progresses(request.user)
    ctx = {}
    for module in module_progresses:
        if module.slug == module_slug:
            ctx['module'] = module
            break
    return render(request, 'dashboard/certificate.html', ctx)


@login_required
def home(request):
    subcriptions = Subscription.objects.filter(
        subscriber=request.user
    ).order_by('-updated_at').prefetch_related('subscription_types').all()
    ctx = {'subscriptions': subcriptions}
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
            user_domain.activate_user(user, None)
        topic_id = int(request.POST['topic'])
        current_topic_duration = Topic.objects.values('duration').get(id=topic_id)['duration']
        maybe_new_topic_duration = form.cleaned_data['topic_duration']
        if current_topic_duration != maybe_new_topic_duration:
            Topic.objects.filter(id=topic_id).update(duration=maybe_new_topic_duration)
        form.save()
        data = form.cleaned_data
        if data['max_watched_time'] >= data['topic_duration']:
            content_statistics_domain.tag_newly_completed_contents.delay(user.id, topic_id)
        return JsonResponse({'msg': 'ok'})
