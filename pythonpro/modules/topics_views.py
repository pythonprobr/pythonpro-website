from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from rolepermissions.checkers import has_object_permission

from pythonpro.memberkit import facade as memberkit_facade
from pythonpro.modules import facade
from pythonpro.modules.models import Content


def content_landing_page(content: Content):
    redirect_path = reverse('checkout:bootcamp_lp')
    return redirect(redirect_path, permanent=False)


@login_required
def old_detail(request, slug):
    topic = facade.get_topic_with_contents(slug=slug)
    return redirect(topic.get_absolute_url(), permanent=True)


@login_required
def detail(request, module_slug, topic_slug):  # noqa
    user = request.user
    if memberkit_facade.has_memberkit_account(user):
        return redirect(facade.get_topic_memberkit_url(topic_slug), permanent=True)
    if memberkit_facade.has_any_subscription(user):
        return redirect(reverse('migrate_to_memberkit'), permanent=True)
    topic = facade.get_topic_with_contents(slug=topic_slug)
    if has_object_permission('access_content', user, topic):
        return render(request, 'topics/topic_detail.html', {'topic': topic})
    return content_landing_page(topic)
