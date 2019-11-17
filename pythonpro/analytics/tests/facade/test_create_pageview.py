import pytest
from model_mommy import mommy

from pythonpro.analytics.models import PageView


def test_should_facade_exists():
    from pythonpro.analytics.facade import create_pageview


@pytest.fixture
def user_session():
    return mommy.make('UserSession')


@pytest.fixture
def create_pageview(user_session, mocked_request):
    from pythonpro.analytics.facade import create_pageview

    return create_pageview(user_session, mocked_request)


@pytest.fixture
def create_pageview_2(user_session, mocked_request):
    from pythonpro.analytics.facade import create_pageview

    return create_pageview(user_session, mocked_request)


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