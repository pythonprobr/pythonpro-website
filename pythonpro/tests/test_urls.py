from pythonpro.urls import urlpatterns


def test_urls_len():
    assert 17 == len(urlpatterns)
