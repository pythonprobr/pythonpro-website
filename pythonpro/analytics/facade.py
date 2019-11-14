from pythonpro.analytics.models import UserSession


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
