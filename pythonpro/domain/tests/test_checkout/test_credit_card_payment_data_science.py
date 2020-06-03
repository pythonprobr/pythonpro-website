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
        rsps.add(responses.GET, f'https://api.pagar.me/1/transactions/{TOKEN}', json=transaction_json)
        rsps.add(responses.POST, f'https://api.pagar.me/1/transactions/{TOKEN}/capture', json=captura_json)
        yield rsps


TRANSACTION_ID = 7656690
TOKEN = 'test_transaction_aJx9ibUmRqYcQrrUaNtQ3arTO4tF1z'


@pytest.fixture
def create_or_update_data_scientist_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.user_facade._email_marketing_facade.create_or_update_data_scientist.delay',
        side_effect=email_marketing_facade.create_or_update_data_scientist
    )


@pytest.fixture
def create_or_update_lead_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.user_facade._email_marketing_facade.create_or_update_lead.delay',
        side_effect=email_marketing_facade.create_or_update_lead
    )


@pytest.fixture
def payment_handler_task_mock(mocker):
    return mocker.patch(
        'pythonpro.domain.checkout_domain.payment_handler_task.delay',
        side_effect=checkout_domain.payment_handler_task
    )


# test user not logged

@pytest.fixture
def resp(client, pagarme_responses, payment_handler_task_mock, create_or_update_lead_mock,
         create_or_update_data_scientist_mock, data_science_item):
    return client.get(reverse('django_pagarme:capture', kwargs={'token': TOKEN, 'slug': data_science_item.slug}),
                      secure=True)


def test_status_code(resp, data_science_item):
    assert resp.status_code == 302
    assert resp.url == reverse('django_pagarme:thanks', kwargs={'slug': data_science_item.slug})


def test_user_is_created(resp, django_user_model):
    User = django_user_model
    assert User.objects.exists()


def test_user_is_webdev(resp, django_user_model):
    User = django_user_model
    user = User.objects.first()
    assert core_facade.is_data_scientist(user)


def test_payment_linked_with_created_user(resp, django_user_model):
    User = django_user_model
    user = User.objects.first()
    payment = django_pagarme_facade.find_payment_by_transaction(str(TRANSACTION_ID))
    assert user == payment.user


# Tests user logged

@pytest.fixture
def resp_logged_user(client_with_user, pagarme_responses, payment_handler_task_mock, data_science_item):
    return client_with_user.get(
        reverse('django_pagarme:capture', kwargs={'token': TOKEN, 'slug': data_science_item.slug}),
        secure=True
    )


def test_logged_user_become_webdev(resp_logged_user, logged_user):
    assert core_facade.is_data_scientist(logged_user)


def test_payment_linked_with_logged_user(resp_logged_user, logged_user):
    payment = django_pagarme_facade.find_payment_by_transaction(TRANSACTION_ID)
    assert logged_user == payment.user


@pytest.fixture
def transaction_json(data_science_item):
    return {
        'object': 'transaction', 'status': 'authorized', 'refuse_reason': None, 'status_reason': 'antifraud',
        'acquirer_response_code': '0000', 'acquirer_name': 'pagarme', 'acquirer_id': '5cdec7071458b442125d940b',
        'authorization_code': '727706', 'soft_descriptor': None, 'tid': TRANSACTION_ID, 'nsu': TRANSACTION_ID,
        'date_created': '2020-01-21T01:10:13.015Z', 'date_updated': '2020-01-21T01:10:13.339Z',
        'amount': data_science_item.price,
        'authorized_amount': data_science_item.price, 'paid_amount': 0, 'refunded_amount': 0, 'installments': 1,
        'id': TRANSACTION_ID, 'cost': 70,
        'card_holder_name': 'Bar Baz', 'card_last_digits': '1111', 'card_first_digits': '411111', 'card_brand': 'visa',
        'card_pin_mode': None, 'card_magstripe_fallback': False, 'cvm_pin': False, 'postback_url': None,
        'payment_method': 'credit_card', 'capture_method': 'ecommerce', 'antifraud_score': None, 'boleto_url': None,
        'boleto_barcode': None, 'boleto_expiration_date': None, 'referer': 'encryption_key', 'ip': '177.27.238.139',
        'items': [{
            'object': 'item',
            'id': f'{data_science_item.slug}',
            'title': f'{data_science_item.name}',
            'unit_price': data_science_item.price,
            'quantity': 1, 'category': None, 'tangible': False, 'venue': None, 'date': None
        }], 'card': {
            'object': 'card', 'id': 'card_ck5n7vtbi010or36dojq96sb1', 'date_created': '2020-01-21T01:45:57.294Z',
            'date_updated': '2020-01-21T01:45:57.789Z', 'brand': 'visa', 'holder_name': 'agora captura',
            'first_digits': '411111', 'last_digits': '1111', 'country': 'UNITED STATES',
            'fingerprint': 'cj5bw4cio00000j23jx5l60cq', 'valid': True, 'expiration_date': '1227'
        }
    }


@pytest.fixture
def captura_json(data_science_item):
    return {
        'object': 'transaction', 'status': 'paid', 'refuse_reason': None, 'status_reason': 'acquirer',
        'acquirer_response_code': '0000', 'acquirer_name': 'pagarme', 'acquirer_id': '5cdec7071458b442125d940b',
        'authorization_code': '408324', 'soft_descriptor': None, 'tid': TRANSACTION_ID, 'nsu': TRANSACTION_ID,
        'date_created': '2020-01-21T01:45:57.309Z', 'date_updated': '2020-01-21T01:47:27.105Z', 'amount': 8000,
        'authorized_amount': data_science_item.price,
        'paid_amount': data_science_item.price, 'refunded_amount': 0,
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
            'id': f'{data_science_item.slug}',
            'title': f'{data_science_item.name}',
            'unit_price': data_science_item.price,
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
