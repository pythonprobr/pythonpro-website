import pytest
import responses
from django.urls import reverse
from rolepermissions.checkers import has_role

from pythonpro.domain import user_facade
from pythonpro.payments.facade import MEMBERSHIP_PRICE

transaction_url = 'https://api.pagar.me/1/transactions/test_transaction_5ndnWcHEJQX1FPCbEpQpFng90gM5oM/capture'
transaction_find_url = 'https://api.pagar.me/1/transactions/test_transaction_5ndnWcHEJQX1FPCbEpQpFng90gM5oM'
transaction_data = {'amount': MEMBERSHIP_PRICE, 'api_key': 'ak_test_6yd4kbaJrWzdn61m4De5yzn7jZuTt9'}

CUSTOMER_EMAIL = 'renzon@gmail.com'
CUSTOMER_FIRST_NAME = 'Renzo'
transaction_response = {
    'object': 'transaction',
    'status': 'paid',
    'refuse_reason': None,
    'status_reason': 'acquirer',
    'acquirer_response_code': '0000',
    'acquirer_name': 'pagarme',
    'acquirer_id': '5cdec7071458b442125d940b',
    'authorization_code': '27373',
    'soft_descriptor': None,
    'tid': 6402263,
    'nsu': 6402263,
    'date_created': '2019-05-26T21:01:53.128Z',
    'date_updated': '2019-05-26T21:25:08.858Z',
    'amount': MEMBERSHIP_PRICE,
    'authorized_amount': MEMBERSHIP_PRICE,
    'paid_amount': MEMBERSHIP_PRICE,
    'refunded_amount': 0,
    'installments': 1,
    'id': 6402263,
    'cost': 100,
    'card_holder_name': 'foo bar',
    'card_last_digits': '1111',
    'card_first_digits': '111111',
    'card_brand': 'mastercard',
    'card_pin_mode': None,
    'card_magstripe_fallback': False,
    'postback_url': None,
    'payment_method': 'credit_card',
    'capture_method': 'ecommerce',
    'antifraud_score': None,
    'boleto_url': None,
    'boleto_barcode': None,
    'boleto_expiration_date': None,
    'referer': 'encryption_key',
    'ip': '187.2.135.31',
    'subscription_id': None,
    'phone': None,
    'address': None,
    'customer': {
        'object': 'customer',
        'id': 2082255,
        'external_id': CUSTOMER_EMAIL,
        'type': 'individual',
        'country': 'br',
        'document_number': None,
        'document_type': 'cpf',
        'name': f'{CUSTOMER_FIRST_NAME} dos Santos Nuccitelli',
        'email': CUSTOMER_EMAIL,
        'phone_numbers': ['+5512997411854'],
        'born_at': None,
        'birthday': None,
        'gender': None,
        'date_created': '2019-05-26T21:01:53.035Z',
        'documents': [{
            'object': 'document',
            'id': 'doc_cjw5fhwkj0cly1y6esw8bj9l3',
            'type': 'cpf',
            'number': '11111111111'
        }]
    },
    'billing': {
        'object': 'billing',
        'id': 991964,
        'name': 'Renzo dos Santos Nuccitelli',
        'address': {
            'object': 'address',
            'street': 'Rua Curacao',
            'complementary': 'Sem complemento',
            'street_number': '494',
            'neighborhood': 'Cidade Vista Verde',
            'city': 'São José dos Campos',
            'state': 'SP',
            'zipcode': '12223750',
            'country': 'br',
            'id': 2275947
        }
    },
    'shipping': None,
    'items': [{
        'object': 'item',
        'id': '6',
        'title': 'Curso Python Pro Turma Bruno Rocha',
        'unit_price': MEMBERSHIP_PRICE,
        'quantity': 1,
        'category': None,
        'tangible': False,
        'venue': None,
        'date': None
    }],
    'card': {
        'object': 'card',
        'id': 'card_cjw5fhwm20clz1y6ecpw44rm2',
        'date_created': '2019-05-26T21:01:53.114Z',
        'date_updated': '2019-05-26T21:01:53.645Z',
        'brand': 'mastercard',
        'holder_name': 'renzo s nuccitelli',
        'first_digits': '111111',
        'last_digits': '111111',
        'country': 'BRAZIL',
        'fingerprint': 'cjw52p1h40zyf0i71t8vwafz7',
        'valid': True,
        'expiration_date': '1025'
    },
    'split_rules': None,
    'metadata': {},
    'antifraud_metadata': {},
    'reference_key': None,
    'device': None,
    'local_transaction_id': None,
    'local_time': None,
    'fraud_covered': False,
    'order_id': None,
    'risk_level': 'very_low',
    'receipt_url': None,
    'payment': None,
    'addition': None,
    'discount': None
}

transaction_response_error = {
    'errors': [{
        'type': 'not_found',
        'parameter_name': None,
        'message': 'Transaction não encontrado'
    }],
    'url': '/transactions/test_transaction_5ndnWcHEJQX1FPCbEpQpFng90gM5oM/capture',
    'method': 'post'
}


@pytest.fixture
def create_or_update_member(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.create_or_update_member')


@pytest.fixture
def tag_as_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.tag_as')


@pytest.fixture
def create_or_update_lead(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.create_or_update_lead')


@pytest.fixture
def resps_success():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as r:
        r.add(r.POST, transaction_url, json=transaction_response, status=200)
        r.add(r.GET, transaction_find_url, json=transaction_response, status=200)
        yield r


@pytest.fixture
def resp_token_with_no_user(cohort, client, create_or_update_member, create_or_update_lead, resps_success, tag_as_mock):
    data = {'token': 'test_transaction_5ndnWcHEJQX1FPCbEpQpFng90gM5oM', 'payment_method': 'credit_card'}
    return client.post(reverse('payments:member_capture'), data, secure=True)


@pytest.fixture
def resp_token(cohort, client_with_lead, logged_user, create_or_update_member, resps_success, tag_as_mock):
    data = {'token': 'test_transaction_5ndnWcHEJQX1FPCbEpQpFng90gM5oM', 'payment_method': 'credit_card'}
    return client_with_lead.post(reverse('payments:member_capture'), data, secure=True)


def test_email_marketing_update(resp_token, create_or_update_member, logged_user):
    create_or_update_member.assert_called_once_with(logged_user.first_name, logged_user.email, id=logged_user.id)


def test_user_become_member(resp_token, logged_user):
    assert has_role(logged_user, 'member')
    assert not has_role(logged_user, 'lead')
    assert not has_role(logged_user, 'client')


def test_user_become_member_interaction(resp_token, logged_user):
    assert 'BECOME_MEMBER' == user_facade.find_user_interactions(logged_user)[0].category


def test_user_registered_to_last_cohort(cohort, resp_token, logged_user):
    assert cohort.students.first() == logged_user


def test_user_tagged_with_cohort_slug(cohort, resp_token, logged_user, tag_as_mock):
    tag_as_mock.assert_called_once_with(logged_user.email, logged_user.id, f'turma-{cohort.slug}')


def test_redirect_url(resp_token):
    assert resp_token.json() == {'redirect_url': '/pagamento/curso-completo/obrigado/'}


def test_ty_status_code(cohort, client):
    assert client.get(reverse('payments:membership_thanks'), secure=True).status_code == 200


def test_user_creation(resp_token_with_no_user, django_user_model):
    user = django_user_model.objects.get(email=CUSTOMER_EMAIL)
    assert has_role(user, 'member')
    assert not has_role(user, 'lead')
    assert not has_role(user, 'client')


def test_user_name(resp_token_with_no_user, django_user_model):
    user = django_user_model.objects.get(email=CUSTOMER_EMAIL)
    assert user.first_name == CUSTOMER_FIRST_NAME


def test_client_update_on_mail_chimp(resp_token_with_no_user, django_user_model, create_or_update_member):
    user = django_user_model.objects.get(email=CUSTOMER_EMAIL)
    create_or_update_member.assert_called_once_with(CUSTOMER_FIRST_NAME, CUSTOMER_EMAIL, id=user.id)


def test_client_lead_not_created_on_email_marketing(resp_token_with_no_user, django_user_model, create_or_update_lead):
    assert create_or_update_lead.call_count == 0
