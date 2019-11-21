import pytest

from pythonpro.analytics.models import UserSession, PageView


def test_should_assert_that_middleware_exists():
    from pythonpro.analytics import middleware
    assert middleware.AnalyticsMiddleware


@pytest.fixture
def mocked_get_or_create_session(mocked_request_with_analytics, mocker):
    return mocker.patch('pythonpro.analytics.middleware.get_or_create_session',
                        return_value=mocked_request_with_analytics)


@pytest.mark.django_db
def test_should_execute_get_or_create_session(client,
                                              mocked_get_or_create_session):

    client.get('/', secure=True)
    assert mocked_get_or_create_session.called


@pytest.fixture
def mocked_create_pageview(mocked_request_with_analytics, mocker):
    return mocker.patch('pythonpro.analytics.middleware.create_pageview',
                        return_value=mocked_request_with_analytics)


@pytest.mark.django_db
def test_should_execute_create_pageview(client, mocked_get_or_create_session,
                                        mocked_create_pageview):

    client.get('/', secure=True)
    assert mocked_create_pageview.called


@pytest.mark.django_db
def test_should_run_full_process(client):
    client.get('/curso-de-python-gratis', secure=True)
    assert UserSession.objects.get()
    assert PageView.objects.get()
