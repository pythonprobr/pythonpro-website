import pytest
from django.urls import reverse


@pytest.fixture
def video_resp(client):
    return client.get(
        reverse(viewname='promos:video', args=('any',)),
    )


def test_video_status(video_resp):
    assert 301 == video_resp.status_code
    assert video_resp.url == reverse('core:lead_landing')
