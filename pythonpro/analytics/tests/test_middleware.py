import pytest


def test_should_assert_that_middleware_exists():
    from pythonpro.analytics.middleware import AnalyticsMiddleware


@pytest.mark.django_db
def test_should_execute_get_or_create_session(client, mocked_request, mocker):
    mocked = mocker.patch(
        'pythonpro.analytics.middleware.get_or_create_session',
        return_value=mocked_request)

    client.get('/', follow=True)
    assert mocked.called


def test_should_execute_create_pagewview():
    assert False