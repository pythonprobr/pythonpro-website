import pytest


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

    client.get('/', follow=True)
    assert mocked_get_or_create_session.called


@pytest.fixture
def mocked_create_pageview(mocked_request_with_analytics, mocker):
    return mocker.patch('pythonpro.analytics.middleware.create_pageview',
                        return_value=mocked_request_with_analytics)


@pytest.mark.django_db
def test_should_execute_create_pageview(client, mocked_get_or_create_session,
                                        mocked_create_pageview):

    client.get('/', follow=True)
    assert mocked_create_pageview.called
