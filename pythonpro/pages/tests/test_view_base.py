from unittest import mock

import pytest

from pythonpro.pages.views import BaseLandingPageView


class TestView(BaseLandingPageView):
    success_url = '/'
    email_marketing_tag = 'test-tag'
    request = mock.Mock()
    request.session.session_key = '1234'
    __test__ = False


def test_should_return_default_template_name():
    assert TestView().get_template_names() == ['pages/test_view.html']


@pytest.fixture
def form():
    form = mock.Mock()
    form.cleaned_data = {'name': 'Moacir', 'email': 'moacir@python.pro.br'}
    return form


def test_should_send_email_to_active_campaign_with_defined_tag(mocker, form):
    mocked = mocker.patch('pythonpro.domain.subscription_domain.subscribe_with_no_role.delay')

    TestView().form_valid(form)
    mocked.assert_called_with('1234', 'Moacir', 'moacir@python.pro.br', 'test-tag')
