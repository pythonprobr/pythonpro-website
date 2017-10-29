import pytest


@pytest.fixture()
def home_resp(client):
    return client.get('/')


def test_home_status_code(home_resp):
    assert 200 == home_resp.status_code


def test_home_template(home_resp):
    assert 'core/index.html' == home_resp.templates[0].name


@pytest.mark.parametrize(
    'form_content',
    [
        '<form action="/interessados/" method="post"',
        '<input type="text" name="name"',
        '<input type="email" name="email"',
        '<button type="submit"'
    ]
)
def test_lead_form(form_content, dj_assert_contains, home_resp):
    dj_assert_contains(home_resp, form_content)
