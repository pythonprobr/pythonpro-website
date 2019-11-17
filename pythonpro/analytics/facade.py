import json

from pythonpro.analytics.models import UserSession, PageView


def get_or_create_session(request):
    if 'analytics_session' in request.session:
        try:
            session = UserSession.objects.get(
                uuid=request.session['analytics_session'])
            return request
        except UserSession.DoesNotExists:
            pass

    session = UserSession.objects.create()
    request.session['analytics_session'] = str(session.uuid)
    return request


def _get_serialized_meta(meta):
    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                return json.JSONEncoder.default(self, obj)
            except TypeError:
                return None

    return json.loads(json.dumps(meta, cls=ComplexEncoder))


def create_pageview(user_session, request):
    PageView.objects.create(session=user_session,
                            meta=_get_serialized_meta(request.META))
