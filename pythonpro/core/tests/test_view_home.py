from datetime import date

import pytest


@pytest.fixture
def home_resp(client):
    yield client.get('/')


def test_home_status_code(home_resp):
    assert 200 == home_resp.status_code


def test_home_template(dj_assert_template_used):
    dj_assert_template_used(template_name='core/index.html')


@pytest.mark.parametrize(
    'form_content',
    [
        '<form action="https://python.us17.list-manage.com/subscribe/post?u=ff7c56095f83f9c254edd749e&amp;id'
        '=e3072e0df0"',
        '<form class="form-inline justify-content-center" '
        'action="https://python.us17.list-manage.com/subscribe/post?u=ff7c56095f83f9c254edd749e&amp;id=a88d1dd555"',
        'method="post"',
        '<input type="text" name="FNAME"',
        '<input type="email" name="EMAIL"',
        '<button type="submit"'
    ]
)
def test_lead_form(form_content, dj_assert_contains, home_resp):
    dj_assert_contains(home_resp, form_content)


@pytest.mark.parametrize(
    'name,value',
    [
        ('day', date.today().strftime('%d')),
        ('month', date.today().strftime('%m')),
        ('year', date.today().strftime('%Y')),
    ]
)
def test_subscription_today_date(name, value, dj_assert_contains, home_resp):
    value = f'<input type="hidden" name="SUBSCRIP[{name}]" value="{value}"'
    dj_assert_contains(home_resp, value)
