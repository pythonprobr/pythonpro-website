from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from pythonpro.dashboard.forms import TopicInteractionForm
from pythonpro.dashboard.models import TopicInteraction


@login_required
def home(request):
    interactions = TopicInteraction.objects.select_related('topic').filter(user=request.user).order_by('-creation')[:20]
    return render(request, 'dashboard/home.html', {'interactions': interactions})


@login_required
@csrf_exempt
def topic_interation(request):
    data = dict(request.POST.items())
    data['user'] = request.user.id
    form = TopicInteractionForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse({'msg': 'ok'})
