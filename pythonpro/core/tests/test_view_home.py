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
        '<form action="/interessados/" method="post"',
        '<input type="text" name="name"',
        '<input type="email" name="email"',
        '<button type="submit"'
    ]
)
def test_lead_form(form_content, dj_assert_contains, home_resp):
    dj_assert_contains(home_resp, form_content)
