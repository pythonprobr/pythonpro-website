def test_should_assert_that_middleware_exists():
    from pythonpro.analytics.middleware import AnalyticsMiddleware


# def test_should_execute_middleware_when_request_is_made(client, mocker):
#     mocked = mocker.patch(
#         'pythonpro.analytics.middleware.AnalyticsMiddleware.process_response')

#     client.get('/')
#     assert mocked.called
