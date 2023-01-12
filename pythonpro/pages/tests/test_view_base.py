from unittest import mock

import pytest
from django.urls import reverse

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
def subscribe_with_no_role(mocker):
    return mocker.patch('pythonpro.pages.views.create_or_update_with_no_role.delay')


def test_should_send_utm_tags_to_active_campaign(client, subscribe_with_no_role):
    client.post(
        reverse('pages:ds_webinar_landing_page') + "?utm_source=test&utm_medium=test",
        {'name': 'Moacir', 'email': 'moacir@python.pro.br'},
        secure=True
    )

    subscribe_with_no_role.assert_called_with(
        'Moacir',
        'moacir@python.pro.br',
        'webinario-data-science',
        'utm_source=test',
        'utm_medium=test',
    )
