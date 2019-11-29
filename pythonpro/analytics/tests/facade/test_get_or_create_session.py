import pytest

from pythonpro.analytics.facade import get_or_create_session
from pythonpro.analytics.models import UserSession


@pytest.fixture
def request_created_in_fixture(mocked_request):
    return get_or_create_session(mocked_request)


@pytest.mark.django_db
def test_should_create_session(request_created_in_fixture):
    assert 'analytics' in request_created_in_fixture.session


@pytest.mark.django_db
def test_should_create_an_usersession_on_database(request_created_in_fixture):
    session = UserSession.objects.get()
    assert request_created_in_fixture.session['analytics'] == {
        'id': session.id,
        'uuid': str(session.uuid)
    }


@pytest.mark.django_db
def test_should_not_assert_any_user_when_has_no_logged_in(
        request_created_in_fixture):
    assert UserSession.objects.get().user is None


@pytest.mark.django_db
def test_should_create_only_one_usersession_per_session(mocked_request):
    request1 = get_or_create_session(mocked_request)
    request2 = get_or_create_session(mocked_request)
    assert request1.session['analytics'] == request2.session['analytics']


@pytest.fixture
def new_request_created_in_fixture(mocked_request_2):
    return get_or_create_session(mocked_request_2)


@pytest.mark.django_db
def test_should_create_two_sessions_for_each_different_visitors(
        new_request_created_in_fixture, request_created_in_fixture):
    assert UserSession.objects.all().count() == 2


@pytest.fixture
def request_created_in_fixture_with_logged_user(mocked_request_logged):
    return get_or_create_session(mocked_request_logged)


@pytest.mark.django_db
def test_should_associate_logged_user_to_a_new_usersession(
        logged_user, request_created_in_fixture_with_logged_user):
    assert UserSession.objects.get().user == logged_user


@pytest.mark.django_db
def test_should_associate_logged_user_to_a_existing_usersession(
        mocked_request, logged_user):
    request = get_or_create_session(mocked_request)
    request.user = logged_user
    get_or_create_session(request)

    assert UserSession.objects.get().user == logged_user
