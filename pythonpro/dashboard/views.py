from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from pythonpro.dashboard.forms import TopicInteractionForm


@csrf_exempt
def topic_interation(request):
    data = dict(request.POST.items())
    data['user'] = request.user.id
    form = TopicInteractionForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse({'msg': 'ok'})
