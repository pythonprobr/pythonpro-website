from pythonpro.urls import urlpatterns


def test_urls_len():
    assert 3 == len(urlpatterns)
