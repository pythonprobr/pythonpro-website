import json

from pythonpro.analytics.models import UserSession, PageView


def _create_session(request):
    user = request.user if not request.user.is_anonymous else None
    session = UserSession.objects.create(user=user)
    return session


def _associate_logged_user_to_session(session, request):
    if not request.user.is_anonymous and not session.user:
        session.user = request.user
        session.save()


def _is_session_setted(request):
    if 'analytics' in request.session:
        try:
            session = UserSession.objects.get(
                id=request.session['analytics']['id'])
            _associate_logged_user_to_session(session, request)
            return True
        except Exception:
            pass

    return False


def get_or_create_session(request):
    if _is_session_setted(request):
        return request

    session = _create_session(request)
    request.session['analytics'] = {
        'id': session.id,
        'uuid': str(session.uuid)
    }
    return request


def _get_serialized_meta(meta):
    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                return json.JSONEncoder.default(self, obj)
            except TypeError:
                return None

    return json.loads(json.dumps(meta, cls=ComplexEncoder))


def _is_to_save_this_pageview(url):
    if url.startswith('/admin'):
        return False
    return True


def create_pageview(request):
    url = request.META.get('PATH_INFO') or ''
    if _is_to_save_this_pageview(url):
        user_session_id = request.session['analytics']['id']
        PageView.objects.create(session_id=user_session_id,
                                meta=_get_serialized_meta(request.META))
