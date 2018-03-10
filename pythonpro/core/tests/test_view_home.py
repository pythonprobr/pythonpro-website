from datetime import date

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains, dj_assert_template_used, dj_assert_not_contains


@pytest.fixture
def home_resp(client):
    return client.get('/')


@pytest.fixture
def home_resp_with_user(django_user_model, client: Client):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return home_resp(client)


def test_home_status_code(home_resp):
    assert 200 == home_resp.status_code


def test_thanks_status_code(client):
    resp = client.get(reverse('core:thanks'))
    assert 200 == resp.status_code


def test_home_template():
    dj_assert_template_used(template_name='core/index.html')


@pytest.mark.parametrize(
    'form_content',
    [
        '<form action="https://python.us17.list-manage.com/subscribe/post?u=ff7c56095f83f9c254edd749e&amp;id'
        '=e3072e0df0"',
        '<input type="text" name="FNAME"',
        '<input type="email" name="EMAIL"',
        '<button type="submit"'
    ]
)
def test_lead_form(form_content, home_resp):
    dj_assert_contains(home_resp, form_content)


@pytest.mark.parametrize(
    'name,value',
    [
        ('day', date.today().strftime('%d')),
        ('month', date.today().strftime('%m')),
        ('year', date.today().strftime('%Y')),
    ]
)
def test_subscription_today_date(name, value, home_resp):
    value = f'<input type="hidden" name="SUBSCRIP[{name}]" value="{value}"'
    dj_assert_contains(home_resp, value)


def test_forum_tab_is_not_present(home_resp):
    """
    Assert Forum tab is no present when user is not logged in
    """
    dj_assert_not_contains(home_resp, f'href="{settings.DISCOURSE_BASE_URL}"')


def test_forum_tab_is_present(home_resp_with_user):
    """
    Assert Forum tab is present when user is logged in
    """
    dj_assert_contains(home_resp_with_user, f'href="{settings.DISCOURSE_BASE_URL}"')
