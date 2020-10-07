import pytest

from model_bakery import baker


@pytest.mark.django_db
def test_should_exists_session_model():
    assert baker.make('UserSession')


@pytest.mark.django_db
def test_should_exists_page_view_model():
    assert baker.make('PageView', meta={'name': 'Renzo'})
