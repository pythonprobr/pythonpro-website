import pytest
from django.urls import reverse
from model_mommy import mommy

from pythonpro.promos.models import Video


@pytest.fixture
def video_resp(client, video):
    return client.get(
        reverse(viewname='promos:video', args=(video.slug,)),
    )


@pytest.fixture
def video(transactional_db):
    return mommy.make(Video)


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
        '<form class="form-inline justify-content-center" '
        'action="https://python.us17.list-manage.com/subscribe/post?u=ff7c56095f83f9c254edd749e&amp;id=a88d1dd555"',
        'method="post"',
        '<input type="text" name="FNAME"',
        '<input type="email" name="EMAIL"',
        '<button type="submit"'
    ]
)
def test_video_lead_form(content, video_resp, dj_assert_contains):
    dj_assert_contains(video_resp, content)


def test_video_title(video, video_resp, dj_assert_contains):
    dj_assert_contains(video_resp, f'<title>{video.title}</title>')


def test_video_h1(video, video_resp, dj_assert_contains):
    dj_assert_contains(video_resp, f'<h1>{video.title}</h1>')


def test_video_iframe(video, video_resp, dj_assert_contains):
    dj_assert_contains(video_resp, f'<iframe src="https://player.vimeo.com/video/{video.vimeo_id}"')


def test_video_context(video, video_resp):
    assert video == video_resp.context['video']
