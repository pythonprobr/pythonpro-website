from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from rolepermissions.checkers import has_object_permission

from pythonpro.modules import facade
from pythonpro.modules.models import Content


def content_landing_page(content: Content):
    if content.module_slug() in {'pytools', 'django', 'entrevistas-tecnicas'}:
        redirect_path = reverse('checkout:webdev_landing_page')
    else:
        redirect_path = reverse('checkout:bootcamp_lp')
    return redirect(redirect_path, permanent=False)


@login_required
def old_detail(request, slug):
    topic = facade.get_topic_with_contents(slug=slug)
    return redirect(topic.get_absolute_url(), permanent=True)


@login_required
def detail(request, module_slug, topic_slug):  # noqa
    topic = facade.get_topic_with_contents(slug=topic_slug)
    if has_object_permission('access_content', request.user, topic):
        return render(request, 'topics/topic_detail.html', {'topic': topic})
    return content_landing_page(topic)
