import pytest

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory


@pytest.fixture
def pre_request():
    factory = RequestFactory()
    request = factory.get('/', follow=True)
    request.user = AnonymousUser()
    return request


@pytest.fixture
def mocked_request(pre_request):
    middleware = SessionMiddleware()
    middleware.process_request(pre_request)
    pre_request.session.save()
    return pre_request


@pytest.fixture
def mocked_request_2(pre_request):
    middleware = SessionMiddleware()
    middleware.process_request(pre_request)
    pre_request.session.save()

    return pre_request
