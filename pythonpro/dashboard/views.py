from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from pythonpro.dashboard.facade import has_watched_any_topic
from pythonpro.dashboard.forms import TopicInteractionForm
from pythonpro.dashboard.models import TopicInteraction
from pythonpro.domain import user_facade


@login_required
def home(request):
    interactions = TopicInteraction.objects.select_related('topic').filter(user=request.user).order_by('-creation')[:20]
    return render(request, 'dashboard/home.html', {'interactions': interactions})


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
