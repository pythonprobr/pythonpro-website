from unittest import mock

import pytest
import responses
from django.urls import reverse
from django_pagarme import facade as django_pagarme_facade

from pythonpro.core import facade as core_facade
from pythonpro.domain import checkout_domain
from pythonpro.email_marketing import facade as email_marketing_facade


@pytest.fixture
def pagarme_responses(transaction_json, captura_json):
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, f'https://api.pagar.me/1/transactions/{TRANSACTION_ID}', json=transaction_json)
        rsps.add(responses.POST, f'https://api.pagar.me/1/transactions/{TRANSACTION_ID}/capture', json=captura_json)
        yield rsps


TRANSACTION_ID = 7656690


@pytest.fixture
def create_or_update_member_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.user_domain._email_marketing_facade.create_or_update_member.delay',
        side_effect=email_marketing_facade.create_or_update_member
    )


@pytest.fixture
def create_or_update_lead_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.user_domain._email_marketing_facade.create_or_update_lead.delay',
        side_effect=email_marketing_facade.create_or_update_lead
    )


@pytest.fixture
def payment_handler_task_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.checkout_domain.payment_handler_task.delay',
        side_effect=checkout_domain.payment_handler_task
    )


@pytest.fixture
def remove_tags_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain._email_marketing_facade.remove_tags.delay')


@pytest.fixture
def sync_on_discourse_mock(mocker):
    return mocker.patch('pythonpro.domain.user_domain.sync_user_on_discourse.delay')


@pytest.fixture
def create_or_update_webdev_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.user_domain._email_marketing_facade.create_or_update_webdev.delay',
        side_effect=email_marketing_facade.create_or_update_webdev
    )


@pytest.fixture
def create_or_update_data_scientist_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.user_domain._email_marketing_facade.create_or_update_data_scientist.delay',
        side_effect=email_marketing_facade.create_or_update_data_scientist
    )


@pytest.fixture
def create_or_update_bootcamper_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.user_domain._email_marketing_facade.create_or_update_bootcamper.delay',
        side_effect=email_marketing_facade.create_or_update_bootcamper
    )


@pytest.fixture
def create_or_update_pythonist_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.user_domain._email_marketing_facade.create_or_update_pythonista.delay',
        side_effect=email_marketing_facade.create_or_update_pythonista
    )


@pytest.fixture
def send_purchase_notification_mock(mocker):
    return mocker.patch('pythonpro.domain.checkout_domain.send_purchase_notification.delay')


# tests for user not logged

@pytest.fixture
def resp(client, pagarme_responses, payment_handler_task_mock, create_or_update_lead_mock,
         create_or_update_member_mock, create_or_update_webdev_mock, create_or_update_data_scientist_mock,
         create_or_update_bootcamper_mock, active_product_item, remove_tags_mock, sync_on_discourse_mock,
         create_or_update_pythonist_mock, send_purchase_notification_mock):
    return client.get(
        reverse('django_pagarme:capture', kwargs={'token': TRANSACTION_ID, 'slug': active_product_item.slug})
    )


def test_status_code(resp, active_product_item):
    assert resp.status_code == 302
    assert resp.url == reverse('django_pagarme:thanks', kwargs={'slug': active_product_item.slug})


def test_send_purchase_notification(resp, send_purchase_notification_mock, active_product_item):
    if active_product_item.slug.startswith('bootcamp'):
        send_purchase_notification_mock.assert_called_once_with(
            django_pagarme_facade.find_payment_by_transaction(TRANSACTION_ID).id
        )


def test_user_is_created(resp, django_user_model):
    User = django_user_model
    assert User.objects.exists()


def test_user_is_promoted(resp, django_user_model, active_product_item):
    User = django_user_model
    user = User.objects.first()
    slug = active_product_item.slug
    assert_user_promoted(user, slug)


def assert_user_promoted(user, slug):
    if slug.startswith('membership'):
        assert core_facade.is_member(user)
    elif slug.startswith('webdev') or slug == 'treinamento-devpro-webinar':
        assert core_facade.is_webdev(user)
    elif slug.startswith('data-science'):
        assert core_facade.is_data_scientist(user)
    elif slug in {'bootcamp', 'bootcamp-webdev'}:
        assert core_facade.is_bootcamper(user)
        assert core_facade.is_pythonista(user)  # bonus because of full paid price
    elif slug.startswith('bootcamp'):
        assert core_facade.is_bootcamper(user)
    elif slug == 'pacote-proximo-nivel-67-discount':
        assert core_facade.is_pythonista(user)
    else:
        pytest.fail(f'Invalid slug prefix {slug}')


def test_user_is_subscribed_to_cohort(resp, django_user_model, cohort, active_product_item):
    User = django_user_model
    user = User.objects.first()
    slug = active_product_item.slug
    asssert_subscribed_to_cohort(cohort, slug, user)


def asssert_subscribed_to_cohort(cohort, slug, user):
    if not (slug.startswith('webdev') or slug == 'treinamento-devpro-webinar' or slug.startswith(
            'data-science') or slug == 'pacote-proximo-nivel-67-discount'):
        assert cohort.students.first() == user


def test_user_synced_on_discourse(resp, django_user_model, sync_on_discourse_mock, active_product_item, mocker):
    User = django_user_model
    user = User.objects.first()
    if active_product_item.slug in {'bootcamp', 'bootcamp-webdev'}:
        user_sync_call = mocker.call(user.id)
        assert sync_on_discourse_mock.mock_calls == [user_sync_call, user_sync_call]
    else:
        sync_on_discourse_mock.assert_called_once_with(user.id)


def test_payment_linked_with_created_user(resp, django_user_model):
    User = django_user_model
    user = User.objects.first()
    payment = django_pagarme_facade.find_payment_by_transaction(str(TRANSACTION_ID))
    assert user == payment.user


def test_phone_in_the_parameters(resp, create_or_update_lead_mock):
    create_or_update_lead_mock.assert_called_once_with(
        'Agora',
        'captura@gmail.com',
        id=mock.ANY,
        phone='+5512997411854'
    )


# Tests user logged

@pytest.fixture
def resp_logged_user(client_with_user, pagarme_responses, payment_handler_task_mock, active_product_item,
                     remove_tags_mock,
                     sync_on_discourse_mock, create_or_update_member_mock, create_or_update_webdev_mock,
                     create_or_update_data_scientist_mock, create_or_update_bootcamper_mock,
                     create_or_update_pythonist_mock, send_purchase_notification_mock):
    return client_with_user.get(
        reverse('django_pagarme:capture', kwargs={'token': TRANSACTION_ID, 'slug': active_product_item.slug})
    )


def test_logged_user_become_member(resp_logged_user, logged_user, active_product_item):
    assert_user_promoted(logged_user, active_product_item.slug)


def test_payment_linked_with_logged_user(resp_logged_user, logged_user):
    payment = django_pagarme_facade.find_payment_by_transaction(TRANSACTION_ID)
    assert logged_user == payment.user


def test_logged_user_is_subscribed_to_cohort(resp_logged_user, logged_user, cohort, active_product_item):
    asssert_subscribed_to_cohort(cohort, active_product_item.slug, logged_user)


def test_logged_user_is_synced_on_discourse(resp_logged_user, logged_user, sync_on_discourse_mock, active_product_item,
                                            mocker):
    if active_product_item.slug in {'bootcamp', 'bootcamp-webdev'}:
        user_sync_call = mocker.call(logged_user.id)
        assert sync_on_discourse_mock.mock_calls == [user_sync_call, user_sync_call]
    else:
        sync_on_discourse_mock.assert_called_once_with(logged_user.id)


@pytest.fixture
def transaction_json(active_product_item):
    return {
        'object': 'transaction', 'status': 'authorized', 'refuse_reason': None, 'status_reason': 'antifraud',
        'acquirer_response_code': '0000', 'acquirer_name': 'pagarme', 'acquirer_id': '5cdec7071458b442125d940b',
        'authorization_code': '727706', 'soft_descriptor': None, 'tid': TRANSACTION_ID, 'nsu': TRANSACTION_ID,
        'date_created': '2020-01-21T01:10:13.015Z', 'date_updated': '2020-01-21T01:10:13.339Z',
        'amount': active_product_item.price,
        'authorized_amount': active_product_item.price, 'paid_amount': 0, 'refunded_amount': 0, 'installments': 1,
        'id': TRANSACTION_ID, 'cost': 70,
        'card_holder_name': 'Bar Baz', 'card_last_digits': '1111', 'card_first_digits': '411111', 'card_brand': 'visa',
        'card_pin_mode': None, 'card_magstripe_fallback': False, 'cvm_pin': False, 'postback_url': None,
        'payment_method': 'credit_card', 'capture_method': 'ecommerce', 'antifraud_score': None, 'boleto_url': None,
        'boleto_barcode': None, 'boleto_expiration_date': None, 'referer': 'encryption_key', 'ip': '177.27.238.139',
        'items': [{
            'object': 'item',
            'id': f'{active_product_item.slug}',
            'title': f'{active_product_item.name}',
            'unit_price': active_product_item.price,
            'quantity': 1, 'category': None, 'tangible': False, 'venue': None, 'date': None
        }], 'card': {
            'object': 'card', 'id': 'card_ck5n7vtbi010or36dojq96sb1', 'date_created': '2020-01-21T01:45:57.294Z',
            'date_updated': '2020-01-21T01:45:57.789Z', 'brand': 'visa', 'holder_name': 'agora captura',
            'first_digits': '411111', 'last_digits': '1111', 'country': 'UNITED STATES',
            'fingerprint': 'cj5bw4cio00000j23jx5l60cq', 'valid': True, 'expiration_date': '1227'
        },
        'customer': {
            'object': 'customer', 'id': 2601905, 'external_id': 'captura@gmail.com', 'type': 'individual',
            'country': 'br',
            'document_number': None, 'document_type': 'cpf', 'name': 'Agora Captura', 'email': 'captura@gmail.com',
            'phone_numbers': ['+5512997411854'], 'born_at': None, 'birthday': None, 'gender': None,
            'date_created': '2020-01-21T01:45:57.228Z', 'documents': [
                {'object': 'document', 'id': 'doc_ck5n7vta0010nr36d01k1zzzw', 'type': 'cpf', 'number': '29770166863'}]
        }, 'billing': {
            'object': 'billing', 'id': 1135539, 'name': 'Agora Captura', 'address': {
                'object': 'address', 'street': 'Rua Bahamas', 'complementary': 'Sem complemento', 'street_number': '56',
                'neighborhood': 'Cidade Vista Verde', 'city': 'São José dos Campos', 'state': 'SP',
                'zipcode': '12223770',
                'country': 'br', 'id': 2559019
            }
        }, 'shipping': None,
    }


@pytest.fixture
def captura_json(active_product_item):
    return {
        'object': 'transaction', 'status': 'paid', 'refuse_reason': None, 'status_reason': 'acquirer',
        'acquirer_response_code': '0000', 'acquirer_name': 'pagarme', 'acquirer_id': '5cdec7071458b442125d940b',
        'authorization_code': '408324', 'soft_descriptor': None, 'tid': TRANSACTION_ID, 'nsu': TRANSACTION_ID,
        'date_created': '2020-01-21T01:45:57.309Z', 'date_updated': '2020-01-21T01:47:27.105Z', 'amount': 8000,
        'authorized_amount': active_product_item.price,
        'paid_amount': active_product_item.price, 'refunded_amount': 0,
        'installments': 1,
        'id': TRANSACTION_ID,
        'cost': 100,
        'card_holder_name': 'agora captura', 'card_last_digits': '1111', 'card_first_digits': '411111',
        'card_brand': 'visa', 'card_pin_mode': None, 'card_magstripe_fallback': False, 'cvm_pin': False,
        'postback_url': None,
        'payment_method': 'credit_card', 'capture_method': 'ecommerce', 'antifraud_score': None,
        'boleto_url': None, 'boleto_barcode': None, 'boleto_expiration_date': None, 'referer': 'encryption_key',
        'ip': '177.27.238.139', 'subscription_id': None, 'phone': None, 'address': None,
        'customer': {
            'object': 'customer', 'id': 2601905, 'external_id': 'captura@gmail.com', 'type': 'individual',
            'country': 'br',
            'document_number': None, 'document_type': 'cpf', 'name': 'Agora Captura', 'email': 'captura@gmail.com',
            'phone_numbers': ['+5512997411854'], 'born_at': None, 'birthday': None, 'gender': None,
            'date_created': '2020-01-21T01:45:57.228Z', 'documents': [
                {'object': 'document', 'id': 'doc_ck5n7vta0010nr36d01k1zzzw', 'type': 'cpf', 'number': '29770166863'}]
        }, 'billing': {
            'object': 'billing', 'id': 1135539, 'name': 'Agora Captura', 'address': {
                'object': 'address', 'street': 'Rua Bahamas', 'complementary': 'Sem complemento', 'street_number': '56',
                'neighborhood': 'Cidade Vista Verde', 'city': 'São José dos Campos', 'state': 'SP',
                'zipcode': '12223770',
                'country': 'br', 'id': 2559019
            }
        }, 'shipping': None,
        'items': [{
            'object': 'item',
            'id': f'{active_product_item.slug}',
            'title': f'{active_product_item.name}',
            'unit_price': active_product_item.price,
            'quantity': 1, 'category': None, 'tangible': False, 'venue': None, 'date': None
        }], 'card': {
            'object': 'card', 'id': 'card_ck5n7vtbi010or36dojq96sb1', 'date_created': '2020-01-21T01:45:57.294Z',
            'date_updated': '2020-01-21T01:45:57.789Z', 'brand': 'visa', 'holder_name': 'agora captura',
            'first_digits': '411111', 'last_digits': '1111', 'country': 'UNITED STATES',
            'fingerprint': 'cj5bw4cio00000j23jx5l60cq', 'valid': True, 'expiration_date': '1227'
        }, 'split_rules': None, 'metadata': {}, 'antifraud_metadata': {}, 'reference_key': None, 'device': None,
        'local_transaction_id': None, 'local_time': None, 'fraud_covered': False, 'fraud_reimbursed': None,
        'order_id': None, 'risk_level': 'very_low', 'receipt_url': None, 'payment': None, 'addition': None,
        'discount': None, 'private_label': None
    }
