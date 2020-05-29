import pytest
import responses
from django.urls import reverse
from django_pagarme import facade as django_pagarme_facade
from model_mommy import mommy

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
BOLETO_URL = 'www.some.boleto.com'
BOLETO_BARCODE = '123455'


# test user not logged
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


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.checkout_domain.email_marketing_facade.tag_as.delay')


@pytest.fixture
def resp(client, pagarme_responses, create_or_update_lead_mock, payment_handler_task_mock, tag_as_mock,
         membership_item):
    return client.get(reverse('django_pagarme:capture', kwargs={'token': TOKEN, 'slug': membership_item.slug}),
                      secure=True)


def test_status_code(resp):
    assert resp.status_code == 200


def test_user_is_created(resp, django_user_model):
    User = django_user_model
    assert User.objects.exists()


def test_user_is_lead(resp, django_user_model):
    User = django_user_model
    user = User.objects.first()
    assert core_facade.is_lead(user)


def test_payment_linked_with_created_user(resp, django_user_model):
    User = django_user_model
    user = User.objects.first()
    payment = django_pagarme_facade.find_payment_by_transaction(TRANSACTION_ID)
    assert user == payment.user


def test_created_user_tagged_with_boleto(resp, django_user_model, tag_as_mock, webdev_item):
    User = django_user_model
    user = User.objects.first()
    tag_as_mock.assert_called_once_with(user.email, user.id, f'{webdev_item.slug}-boleto')


# Tests user logged

@pytest.fixture
def resp_logged_user(client_with_lead, pagarme_responses, payment_handler_task_mock, tag_as_mock, membership_item):
    return client_with_lead.get(
        reverse('django_pagarme:capture', kwargs={'token': TOKEN, 'slug': membership_item.slug}),
        secure=True
    )


def test_logged_user_become_lead(resp_logged_user, logged_user):
    assert core_facade.is_lead(logged_user)


def test_payment_linked_with_logged_user(resp_logged_user, logged_user):
    payment = django_pagarme_facade.find_payment_by_transaction(TRANSACTION_ID)
    assert logged_user == payment.user


def test_user_tagged_with_boleto(resp_logged_user, logged_user, tag_as_mock, webdev_item):
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, f'{webdev_item.slug}-boleto')


@pytest.fixture
def remove_tags_mock(mocker):
    return mocker.patch('pythonpro.domain.checkout_domain.email_marketing_facade.remove_tags.delay')


def test_payment_tag_removed_after_payment(resp_logged_user, webdev_item, remove_tags_mock, logged_user):
    payment = django_pagarme_facade.find_payment_by_transaction(TRANSACTION_ID)
    mommy.make(django_pagarme_facade.PagarmeNotification, status=django_pagarme_facade.PAID, payment=payment)
    checkout_domain.payment_handler_task(payment.id)
    remove_tags_mock.assert_called_once_with(logged_user.email, logged_user.id, f'{webdev_item.slug}-boleto')


@pytest.fixture
def transaction_json(webdev_item):
    return {
        'object': 'transaction',
        'status': 'authorized',
        'refuse_reason': None,
        'status_reason': 'acquirer',
        'acquirer_response_code': None,
        'acquirer_name': 'pagarme',
        'acquirer_id': '5cdec7071458b442125d940b',
        'authorization_code': None,
        'soft_descriptor': None,
        'tid': TRANSACTION_ID,
        'nsu': TRANSACTION_ID,
        'date_created': '2020-03-07T17:04:58.279Z',
        'date_updated': '2020-03-07T17:04:58.502Z',
        'authorized_amount': webdev_item.price,
        'paid_amount': 0,
        'refunded_amount': 0,
        'installments': 1,
        'id': TRANSACTION_ID,
        'cost': 0,
        'card_holder_name': None,
        'card_last_digits': None,
        'card_first_digits': None,
        'card_brand': None,
        'card_pin_mode': None,
        'card_magstripe_fallback': False,
        'cvm_pin': False,
        'postback_url': 'https://e0f89dca.ngrok.io/django_pagarme/notification',
        'payment_method': 'boleto',
        'capture_method': 'ecommerce',
        'antifraud_score': None,
        'boleto_url': None,
        'boleto_barcode': None,
        'boleto_expiration_date': '2020-03-09T03:00:00.000Z',
        'referer': 'encryption_key',
        'ip': '177.170.213.5',
        'subscription_id': None,
        'phone': None,
        'address': None,
        'customer': {
            'object': 'customer',
            'id': 2725813,
            'external_id': 'foo@email.com',
            'type': 'individual',
            'country': 'br',
            'document_number': None,
            'document_type': 'cpf',
            'name': 'Foo',
            'email': 'foo@email.com',
            'phone_numbers': ['+5512999999999'],
            'born_at': None,
            'birthday': None,
            'gender': None,
            'date_created': '2020-03-07T17:04:58.220Z',
            'documents': [
                {
                    'object': 'document',
                    'id': 'doc_ck7huyv07072mmp6f59af8u8h',
                    'type': 'cpf',
                    'number': '04367331024'
                }]
        },
        'billing': {
            'object': 'billing',
            'id': 1168861,
            'name': 'Foo',
            'address': {
                'object': 'address',
                'street': 'Rua Buenos Aires',
                'complementary': 'Sem complemento',
                'street_number': '7',
                'neighborhood': 'Cidade Vista Verde',
                'city': 'São José dos Campos',
                'state': 'SP',
                'zipcode': '12223730',
                'country': 'br',
                'id': 2641028
            }
        },
        'shipping': None,
        'items': [{
            'object': 'item',
            'id': f'{webdev_item.slug}',
            'title': f'{webdev_item.name}',
            'unit_price': webdev_item.price,
            'quantity': 1,
            'category': None,
            'tangible': False,
            'venue': None,
            'date': None
        }],
        'card': None,
        'split_rules': None,
        'metadata': {},
        'antifraud_metadata': {},
        'reference_key': None,
        'device': None,
        'local_transaction_id': None,
        'local_time': None,
        'fraud_covered': False,
        'fraud_reimbursed': None,
        'order_id': None,
        'risk_level': 'unknown',
        'receipt_url': None,
        'payment': None,
        'addition': None,
        'discount': None,
        'private_label': None
    }


@pytest.fixture
def captura_json(webdev_item):
    return {
        'object': 'transaction',
        'status': 'waiting_payment',
        'refuse_reason': None,
        'status_reason': 'acquirer',
        'acquirer_response_code': None,
        'acquirer_name': 'pagarme',
        'acquirer_id': '5cdec7071458b442125d940b',
        'authorization_code': None,
        'soft_descriptor': None,
        'tid': TRANSACTION_ID,
        'nsu': TRANSACTION_ID,
        'date_created': '2020-03-07T17:04:58.279Z',
        'date_updated': '2020-03-07T17:11:14.957Z',
        'amount': webdev_item.price,
        'authorized_amount': webdev_item.price,
        'paid_amount': 0,
        'refunded_amount': 0,
        'installments': 1,
        'id': TRANSACTION_ID,
        'cost': 0,
        'card_holder_name': None,
        'card_last_digits': None,
        'card_first_digits': None,
        'card_brand': None,
        'card_pin_mode': None,
        'card_magstripe_fallback': False,
        'cvm_pin': False,
        'postback_url': 'https://e0f89dca.ngrok.io/django_pagarme/notification',
        'payment_method': 'boleto',
        'capture_method': 'ecommerce',
        'antifraud_score': None,
        'boleto_url': BOLETO_URL,
        'boleto_barcode': BOLETO_BARCODE,
        'boleto_expiration_date': '2020-03-09T03:00:00.000Z',
        'referer': 'encryption_key',
        'ip': '177.170.213.5',
        'subscription_id': None,
        'phone': None,
        'address': None,
        'customer': {
            'object': 'customer',
            'id': 2725813,
            'external_id': 'foo@email.com',
            'type': 'individual',
            'country': 'br',
            'document_number': None,
            'document_type': 'cpf',
            'name': 'Foo',
            'email': 'foo@email.com',
            'phone_numbers': ['+5512999999999'],
            'born_at': None,
            'birthday': None,
            'gender': None,
            'date_created': '2020-03-07T17:04:58.220Z',
            'documents': [
                {
                    'object': 'document',
                    'id': 'doc_ck7huyv07072mmp6f59af8u8h',
                    'type': 'cpf',
                    'number': '04367331024'
                }]
        },
        'billing': {
            'object': 'billing',
            'id': 1168861,
            'name': 'Foo',
            'address': {
                'object': 'address',
                'street': 'Rua Buenos Aires',
                'complementary': 'Sem complemento',
                'street_number': '7',
                'neighborhood': 'Cidade Vista Verde',
                'city': 'São José dos Campos',
                'state': 'SP',
                'zipcode': '12223730',
                'country': 'br',
                'id': 2641028
            }
        },
        'shipping': None,
        'items': [{
            'object': 'item',
            'id': f'{webdev_item.slug}',
            'title': f'{webdev_item.name}',
            'unit_price': webdev_item.price,
            'quantity': 1,
            'category': None,
            'tangible': False,
            'venue': None,
            'date': None
        }],
        'card': None,
        'split_rules': None,
        'metadata': {},
        'antifraud_metadata': {},
        'reference_key': None,
        'device': None,
        'local_transaction_id': None,
        'local_time': None,
        'fraud_covered': False,
        'fraud_reimbursed': None,
        'order_id': None,
        'risk_level': 'unknown',
        'receipt_url': None,
        'payment': None,
        'addition': None,
        'discount': None,
        'private_label': None
    }
