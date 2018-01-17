import pytest

from django.urls import reverse


@pytest.fixture
def video_resp(client, transactional_db):
    return client.get(
        reverse(viewname='promos:video', args=('motivacao',)),
    )


def test_video_status(video_resp):
    assert 200 == video_resp.status_code


def test_ty_status(client):
    resp = client.get(
        reverse(viewname='promos:thanks'),
    )
    assert 200 == resp.status_code


@pytest.mark.parametrize(
    'content',
    [
        '<title>Motivação</title>',
        '<h1>Motivação</h1>',
        '<iframe src="https://player.vimeo.com/video/251224475"',
        '<form class="form-inline justify-content-center" '
        'action="https://python.us17.list-manage.com/subscribe/post?u=ff7c56095f83f9c254edd749e&amp;id=a88d1dd555"',
        'method="post"',
        '<input type="text" name="FNAME"',
        '<input type="email" name="EMAIL"',
        '<button type="submit"'
    ]
)
def test_video_content(content, video_resp, dj_assert_contains):
    dj_assert_contains(video_resp, content)
