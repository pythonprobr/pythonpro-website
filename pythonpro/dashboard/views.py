from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from pythonpro.dashboard.facade import has_watched_any_topic
from pythonpro.dashboard.forms import TopicInteractionForm
from pythonpro.domain import user_facade
from pythonpro.modules.models import Topic


@login_required
def home(request):
    topics = list(
        Topic.objects.filter(
            topicinteraction__user=request.user
        ).annotate(
            last_interaction=Max('topicinteraction__creation')
        ).annotate(
            max_watched_time=Max('topicinteraction__max_watched_time')
        ).annotate(
            total_watched_time=Sum('topicinteraction__total_watched_time')
        ).annotate(
            interactions_count=Count('topicinteraction')
        ).order_by('-last_interaction').select_related('chapter').select_related('chapter__section').select_related(
            'chapter__section__module')[:20]
    )

    for topic in topics:
        topic.calculated_module = topic.find_module()

    return render(
        request,
        'dashboard/home.html',
        {
            'topics': topics,
        }
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

        form.save()
        return JsonResponse({'msg': 'ok'})
