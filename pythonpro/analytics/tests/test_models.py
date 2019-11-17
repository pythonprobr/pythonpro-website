import pytest

from model_mommy import mommy


@pytest.mark.django_db
def test_should_exists_session_model():
    assert mommy.make('UserSession')


@pytest.mark.django_db
def test_should_exists_page_view_model():
    assert mommy.make('PageView')
