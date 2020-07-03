import pytest
from django.urls import reverse

from pythonpro.core import facade as core_facade
from pythonpro.core.models import UserInteraction
from pythonpro.django_assertions import dj_assert_template_used

all_slugs = pytest.mark.parametrize(
    'slug',
    [
        'membership',
        'membership-client',
        'membership-client-first-day',
        'membership-first-day',
    ]
)


@all_slugs
def test_all_slugs_available(client, slug):
    resp = client.get(reverse('django_pagarme:contact_info', kwargs={'slug': slug}))
    assert resp.status_code == 200


@pytest.fixture(autouse=True)
def create_or_update_with_no_role_mock(mocker):
    return mocker.patch('pythonpro.domain.checkout_domain.email_marketing_facade.create_or_update_with_no_role.delay')


@pytest.fixture
def valid_data():
    return {'name': 'Foo Bar Baz', 'email': 'foo@email.com', 'phone': '12999999999'}


def make_post(client, contact_info, slug):
    return client.post(reverse('django_pagarme:contact_info', kwargs={'slug': slug}), contact_info)


@all_slugs
def test_status_code(resp, client, valid_data, slug):
    resp = make_post(client, valid_data, slug)
    assert resp.status_code == 302


membership_slugs = pytest.mark.parametrize(
    'slug',
    [
        'membership',
        'membership-client',
        'membership-client-first-day',
        'membership-first-day',
    ]
)


@membership_slugs
def test_member_history(client_with_user, valid_data, slug, logged_user):
    make_post(client_with_user, valid_data, slug)
    interactions = core_facade.find_user_interactions(logged_user)
    assert [i.category for i in interactions] == [UserInteraction.MEMBER_CHECKOUT_FORM]


@all_slugs
def test_email_marketing_register(client, valid_data, slug, create_or_update_with_no_role_mock):
    make_post(client, valid_data, slug)
    create_or_update_with_no_role_mock.assert_called_once_with(
        valid_data['name'], valid_data['email'], f'{slug}-form', id=None, phone='+5512999999999'
    )


@all_slugs
def test_email_marketing_update(client_with_user, valid_data, slug, create_or_update_with_no_role_mock, logged_user):
    make_post(client_with_user, valid_data, slug)
    create_or_update_with_no_role_mock.assert_called_once_with(
        valid_data['name'], valid_data['email'], f'{slug}-form', id=logged_user.id, phone='+5512999999999'
    )


@all_slugs
def test_invalid_data(client, slug):
    dct = {'name': 'Foo Bar Baz', 'email': 'foo', 'phone': '129'}
    resp = make_post(client, dct, slug)
    assert resp.status_code == 400
    dj_assert_template_used('django_pagarme/contact_form_errors.html')


webdev_slugs = pytest.mark.parametrize(
    'slug',
    [
        'webdev-oto',
        'webdev',
    ]
)


@webdev_slugs
def test_webdev_history(client_with_user, valid_data, slug, logged_user):
    make_post(client_with_user, valid_data, slug)
    interactions = core_facade.find_user_interactions(logged_user)
    assert [i.category for i in interactions] == [UserInteraction.WEBDEV_CHECKOUT_FORM]
