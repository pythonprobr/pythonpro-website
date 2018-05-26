from unittest.mock import Mock

import pytest
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponseRedirect

from pythonpro.core.middleware import SSLMiddleware


@pytest.fixture
def ssl_middleware_class():
    """ Keeping original class attribute value to isolate tests """
    original_value = SSLMiddleware.debug_flag
    yield SSLMiddleware
    SSLMiddleware.debug_flag = original_value


@pytest.mark.parametrize('debug', [True, False])
def test_ssl_middleware_removed_for_debug_true(debug, mocker, ssl_middleware_class):
    setttings_mock = mocker.patch('pythonpro.core.middleware.settings')
    setttings_mock.DEBUG = True
    ssl_middleware_class.debug_flag = debug

    with pytest.raises(MiddlewareNotUsed):
        ssl_middleware_class(None)

    assert ssl_middleware_class.debug_flag


@pytest.mark.parametrize('debug', [True, False])
def test_ssl_middleware_removed_for_debug_flag(debug, mocker, ssl_middleware_class):
    setttings_mock = mocker.patch('pythonpro.core.middleware.settings')
    setttings_mock.DEBUG = debug
    ssl_middleware_class.debug_flag = True

    with pytest.raises(MiddlewareNotUsed):
        ssl_middleware_class(None)


def test_ssl_redirect_for_unsecure_request(mocker, ssl_middleware_class):
    setttings_mock = mocker.patch('pythonpro.core.middleware.settings')
    setttings_mock.DEBUG = False
    ssl_middleware_class.debug_flag = False
    request = Mock()
    request.is_secure.return_value = False
    request.META.get.return_value = 'http'
    request.build_absolute_uri.return_value = 'http://python.pro.br'
    mid = ssl_middleware_class(None)
    response = mid(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == 'https://python.pro.br'


def test_ssl_no_redirect_for_secure_request(mocker, ssl_middleware_class):
    setttings_mock = mocker.patch('pythonpro.core.middleware.settings')
    setttings_mock.DEBUG = False
    ssl_middleware_class.debug_flag = False
    request = Mock()
    request.is_secure.return_value = True
    request.META.get.return_value = 'http'
    expected_response = Mock()
    get_response = Mock(return_value=expected_response)
    mid = ssl_middleware_class(get_response)
    response = mid(request)
    assert expected_response is response
    get_response.assert_called_once_with(request)


def test_ssl_no_redirect_for_https_heroku_header(mocker, ssl_middleware_class):
    setttings_mock = mocker.patch('pythonpro.core.middleware.settings')
    setttings_mock.DEBUG = False
    ssl_middleware_class.debug_flag = False
    request = Mock()
    request.is_secure.return_value = False
    request.META.get.return_value = 'https'
    expected_response = Mock()
    get_response = Mock(return_value=expected_response)
    mid = ssl_middleware_class(get_response)
    response = mid(request)
    assert expected_response is response
    get_response.assert_called_once_with(request)
    request.META.get.assert_called_once_with('HTTP_X_FORWARDED_PROTO', '')
