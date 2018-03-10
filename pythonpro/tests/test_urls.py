from pythonpro.urls import urlpatterns


def test_urls_len():
    assert 10 == len(urlpatterns)
