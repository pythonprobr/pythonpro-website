import json
import logging

import posthog
from django.conf import settings

from pythonpro.analytics.models import UserSession, PageView


def _create_session(request):
    user = request.user if not request.user.is_anonymous else None
    return UserSession.objects.create(user=user)


def _mount_session_dict(session):
    return {'id': session.id, 'uuid': str(session.uuid)}


def _associate_logged_user_to_session(session_id, user):
    session = UserSession.objects.get(id=session_id)
    if not user.is_anonymous and session.user is None:
        session.user = user
        session.save()


def _setup_analytics_object(request):
    analytics = request.session.get('analytics')
    if analytics is None:
        session = _create_session(request)
        analytics = _mount_session_dict(session)

    _associate_logged_user_to_session(analytics['id'], request.user)
    return analytics


def get_or_create_session(request):
    request.session['analytics'] = _setup_analytics_object(request)
    return request


def _get_serialized_meta(meta):
    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                return json.JSONEncoder.default(self, obj)
            except TypeError:
                return None

    return json.loads(json.dumps(meta, cls=ComplexEncoder))


def _should_create_pageview(url):
    return url.startswith('/admin') is False


def create_pageview(request):
    url = request.META.get('PATH_INFO') or ''
    if _should_create_pageview(url):
        user_session_id = request.session['analytics']['id']
        PageView.objects.create(session_id=user_session_id,
                                meta=_get_serialized_meta(request.META))


def posthog_alias(session_id, email):
    if settings.POSTHOG_API_KEY and settings.POSTHOG_API_URL:
        posthog.alias(session_id, email)
    else:
        logger = logging.getLogger(__name__)
        logger.info(f'The value of session_id is {session_id} and email is {email}')
