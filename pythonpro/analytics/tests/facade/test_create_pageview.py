import pytest

from pythonpro.analytics.models import PageView


def test_should_facade_exists():
    from pythonpro.analytics import facade
    assert facade.create_pageview


@pytest.fixture
def create_pageview(mocked_request_with_analytics):
    from pythonpro.analytics.facade import create_pageview

    return create_pageview(mocked_request_with_analytics)


@pytest.fixture
def create_pageview_2(mocked_request_with_analytics):
    from pythonpro.analytics.facade import create_pageview

    return create_pageview(mocked_request_with_analytics)


@pytest.mark.django_db
def test_should_create_pageview_on_database(create_pageview):
    assert PageView.objects.all().count() == 1


@pytest.mark.django_db
def test_should_create_meta_field_as_dict(create_pageview):
    assert isinstance(PageView.objects.get().meta, dict)


@pytest.mark.django_db
def test_should_create_pageview_for_each_request(create_pageview,
                                                 create_pageview_2):
    assert PageView.objects.all().count() == 2


def test_should_ignore_all_urls_that_starts_with_admin():
    from pythonpro.analytics.facade import _should_create_pageview

    assert _should_create_pageview('/curso-gratis-de-python') is True
    assert _should_create_pageview('/admin/analytics/pageview') is False
    assert _should_create_pageview('/admin') is False


@pytest.mark.django_db
def test_should_call_should_create_pageview_function(
        mocked_request_with_analytics, mocker):
    from pythonpro.analytics.facade import create_pageview

    mocked = mocker.patch('pythonpro.analytics.facade._should_create_pageview',
                          return_value=True)

    create_pageview(mocked_request_with_analytics)
    assert mocked.called
