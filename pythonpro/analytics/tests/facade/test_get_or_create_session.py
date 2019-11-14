import pytest

from pythonpro.analytics.models import UserSession


def test_should_exists_method():
    from pythonpro.analytics.facade import get_or_create_session


@pytest.fixture
def response(client):
    return client.get('/', follow=True)


@pytest.mark.django_db
def test_should_create_session(response, client):
    assert 'analytics_session' in client.session


@pytest.mark.django_db
def test_should_create_an_usersession_on_database(response, client):
    session = UserSession.objects.get()
    assert client.session['analytics_session'] == str(session.uuid)


@pytest.mark.django_db
def test_should_create_only_one_usersession_per_session(response, client):
    client.get('/curso-de-python-gratis', follow=True)

    session = UserSession.objects.get()
    assert client.session['analytics_session'] == str(session.uuid)


@pytest.mark.django_db
def test_should_create_two_sessions_for_each_different_visitors(
        response, client):
    assert False