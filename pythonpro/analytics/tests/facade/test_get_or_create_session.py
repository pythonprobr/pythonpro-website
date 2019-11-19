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
    assert 'analytics' in get_or_create_session.session


@pytest.mark.django_db
def test_should_create_an_usersession_on_database(get_or_create_session):
    session = UserSession.objects.get()
    assert get_or_create_session.session['analytics'] == {
        'id': session.id,
        'uuid': str(session.uuid)
    }


@pytest.mark.django_db
def test_should_not_assert_any_user_when_has_no_logged_in(
        get_or_create_session):
    assert not UserSession.objects.get().user


@pytest.mark.django_db
def test_should_create_only_one_usersession_per_session(mocked_request):
    from pythonpro.analytics.facade import get_or_create_session

    request1 = get_or_create_session(mocked_request)
    request2 = get_or_create_session(mocked_request)

    assert request1.session['analytics'] == request2.session['analytics']


@pytest.fixture
def new_get_or_create_session(mocked_request_2):
    from pythonpro.analytics.facade import get_or_create_session

    return get_or_create_session(mocked_request_2)


@pytest.mark.django_db
def test_should_create_two_sessions_for_each_different_visitors(
        new_get_or_create_session, get_or_create_session):
    assert UserSession.objects.all().count() == 2


@pytest.fixture
def get_or_create_session_with_logged_user(mocked_request_logged):
    from pythonpro.analytics.facade import get_or_create_session

    return get_or_create_session(mocked_request_logged)


@pytest.mark.django_db
def test_should_associate_logged_user_to_a_new_usersession(
        logged_user, get_or_create_session_with_logged_user):
    assert UserSession.objects.get().user == logged_user


@pytest.mark.django_db
def test_should_associate_logged_user_to_a_existing_usersession(
        mocked_request, logged_user):
    from pythonpro.analytics.facade import get_or_create_session

    request = get_or_create_session(mocked_request)
    request.user = logged_user
    get_or_create_session(request)

    assert UserSession.objects.get().user == logged_user
