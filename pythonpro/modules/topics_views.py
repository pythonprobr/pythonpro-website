from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rolepermissions.checkers import has_object_permission

from pythonpro.mailchimp.facade import tag_as
from pythonpro.modules import facade
from pythonpro.modules.models import Content
from pythonpro.modules.permissions import is_client_content
from pythonpro.payments.facade import PYTOOLS_PRICE


def content_landing_page(request, content: Content):
    template = 'topics/content_member_landing_page.html'
    tag = 'potencial-member'
    if is_client_content(content):
        template = 'topics/content_client_landing_page.html'
        tag = 'potencial-client'

    tag_as(request.user.email, tag)
    return render(request, template, {
        'content': content,
        'PAGARME_CRYPTO_KEY': settings.PAGARME_CRYPTO_KEY,
        'price': PYTOOLS_PRICE
    })


@login_required
def old_detail(request, slug):
    topic = facade.get_topic_with_contents(slug=slug)
    return redirect(topic.get_absolute_url(), permanent=True)


@login_required
def detail(request, module_slug, topic_slug):  # noqa
    topic = facade.get_topic_with_contents(slug=topic_slug)
    if has_object_permission('access_content', request.user, topic):
        return render(request, 'topics/topic_detail.html', {'topic': topic})
    return content_landing_page(request, topic)
