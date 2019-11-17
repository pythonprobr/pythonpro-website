import pytest

from django.test import Client

from pythonpro.analytics.models import UserSession


def test_should_exists_method():
    from pythonpro.analytics.facade import get_or_create_session


@pytest.fixture
def get_or_create_session(mocked_request):
    from pythonpro.analytics.facade import get_or_create_session

    return get_or_create_session(mocked_request)


@pytest.mark.django_db
def test_should_create_session(get_or_create_session):
    assert 'analytics_session' in get_or_create_session.session


@pytest.mark.django_db
def test_should_create_an_usersession_on_database(get_or_create_session):
    session = UserSession.objects.get()
    assert get_or_create_session.session['analytics_session'] == str(
        session.uuid)


@pytest.mark.django_db
def test_should_create_only_one_usersession_per_session(mocked_request):
    from pythonpro.analytics.facade import get_or_create_session

    request1 = get_or_create_session(mocked_request)
    request2 = get_or_create_session(mocked_request)

    assert request1.session['analytics_session'] == request2.session[
        'analytics_session']


@pytest.fixture
def new_get_or_create_session(mocked_request_2):
    from pythonpro.analytics.facade import get_or_create_session

    return get_or_create_session(mocked_request_2)


@pytest.mark.django_db
def test_should_create_two_sessions_for_each_different_visitors(
        new_get_or_create_session, get_or_create_session):
    assert UserSession.objects.all().count() == 2


def test_should_associate_logged_user_to_usersession():
    assert False