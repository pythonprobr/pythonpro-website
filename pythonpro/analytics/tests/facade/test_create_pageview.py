import pytest

from pythonpro.analytics.facade import create_pageview, _should_create_pageview
from pythonpro.analytics.models import PageView


@pytest.fixture
def create_pageview_executed(mocked_request_with_analytics):
    return create_pageview(mocked_request_with_analytics)


@pytest.mark.django_db
def test_should_create_pageview_on_database(create_pageview_executed):
    assert PageView.objects.all().count() == 1


@pytest.mark.django_db
def test_should_create_meta_field_as_dict(create_pageview_executed):
    assert isinstance(PageView.objects.get().meta, dict)


@pytest.fixture
def create_pageview_executed_2(mocked_request_with_analytics):
    return create_pageview(mocked_request_with_analytics)


@pytest.mark.django_db
def test_should_create_pageview_for_each_request(create_pageview_executed,
                                                 create_pageview_executed_2):
    assert PageView.objects.all().count() == 2


def test_should_ignore_all_urls_that_starts_with_admin():
    assert _should_create_pageview('/curso-gratis-de-python') is True
    assert _should_create_pageview('/admin/analytics/pageview') is False
    assert _should_create_pageview('/admin') is False


@pytest.mark.django_db
def test_should_call_should_create_pageview_function(
        mocked_request_with_analytics, mocker):
    mocked = mocker.patch('pythonpro.analytics.facade._should_create_pageview',
                          return_value=True)

    create_pageview(mocked_request_with_analytics)
    assert mocked.called
