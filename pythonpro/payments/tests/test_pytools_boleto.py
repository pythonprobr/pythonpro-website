import pytest
import responses
from django.urls import reverse
from model_mommy import mommy
from rolepermissions.checkers import has_role

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.domain import user_facade

transaction_url = 'https://api.pagar.me/1/transactions/test_transaction_QtapRINw2wJdeBbQizns1G6XwIYgrt/capture'
transaction_find_url = 'https://api.pagar.me/1/transactions/test_transaction_QtapRINw2wJdeBbQizns1G6XwIYgrt'
transaction_data = {
    'token': 'test_transaction_QtapRINw2wJdeBbQizns1G6XwIYgrt',
    'payment_method': 'boleto'
}

CUSTOMER_EMAIL = 'daenerys.targaryen@gmail.com'
CUSTOMER_FIRST_NAME = 'DAENERYS'
transaction_response = {
    'object': 'transaction',
    'status': 'waiting_payment',
    'refuse_reason': None,
    'status_reason': 'acquirer',
    'acquirer_response_code': None,
    'acquirer_name': 'pagarme',
    'acquirer_id': '5cdec7071458b442125d940b',
    'authorization_code': None,
    'soft_descriptor': None,
    'tid': 6409891,
    'nsu': 6409891,
    'date_created': '2019-05-28T01:10:54.063Z',
    'date_updated': '2019-05-28T01:17:33.427Z',
    'amount': 9999,
    'authorized_amount': 9999,
    'paid_amount': 0,
    'refunded_amount': 0,
    'installments': 1,
    'id': 6409891,
    'cost': 0,
    'card_holder_name': None,
    'card_last_digits': None,
    'card_first_digits': None,
    'card_brand': None,
    'card_pin_mode': None,
    'card_magstripe_fallback': False,
    'postback_url': None,
    'payment_method': 'boleto',
    'capture_method': 'ecommerce',
    'antifraud_score': None,
    'boleto_url': 'https://api.pagar.me/1/boletos/live_cjw86db172bld2p3en7gy50l6',
    'boleto_barcode': '1234 5678',
    'boleto_expiration_date': '2019-06-03T03:00:00.000Z',
    'referer': 'encryption_key',
    'ip': '201.75.170.145',
    'subscription_id': None,
    'phone': None,
    'address': None,
    'customer': {
        'object': 'customer',
        'id': 2085075,
        'external_id': CUSTOMER_EMAIL,
        'type': 'corporation',
        'country': 'br',
        'document_number': None,
        'document_type': 'cpf',
        'name': f'{CUSTOMER_FIRST_NAME} TARGARYEN',
        'email': CUSTOMER_EMAIL,
        'phone_numbers': ['+5512121212121'],
        'born_at': None,
        'birthday': None,
        'gender': None,
        'date_created': '2019-05-28T01:10:53.981Z',
        'documents': [{
            'object': 'document',
            'id': 'doc_cjw73tzqw02jys26ebuymmihx',
            'type': 'cnpj',
            'number': '18152564000105'
        }]
    },
    'billing': {
        'object': 'billing',
        'id': 993788,
        'name': 'DAENERYS TARGARYEN',
        'address': {
            'object': 'address',
            'street': 'Rua Doutor Geraldo Campos Moreira',
            'complementary': 'Sem complemento',
            'street_number': '454',
            'neighborhood': 'Cidade Monções',
            'city': 'São Paulo',
            'state': 'SP',
            'zipcode': '04571020',
            'country': 'br',
            'id': 2278312
        }
    },
    'shipping': None,
    'items': [{
        'object': 'item',
        'id': '6',
        'title': 'Curso PyTools',
        'unit_price': 9999,
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
    'order_id': None,
    'risk_level': 'unknown',
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
def create_or_update_client(mocker):
    return mocker.patch('pythonpro.domain.user_facade._mailchimp_facade.create_or_update_client')


@pytest.fixture
def create_or_update_lead(mocker):
    return mocker.patch('pythonpro.domain.user_facade._mailchimp_facade.create_or_update_lead')


@pytest.fixture
def resps_success():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as r:
        r.add(r.POST, transaction_url, json=transaction_response, status=200)
        r.add(r.GET, transaction_find_url, json=transaction_response, status=200)
        yield r


@pytest.fixture
def resp_token(client_with_lead, logged_user, create_or_update_client, resps_success):
    return client_with_lead.post(reverse('payments:pytools_capture'), transaction_data, secure=True)


@pytest.fixture
def resp_token_with_no_user(client, create_or_update_client, create_or_update_lead, resps_success, db):
    return client.post(reverse('payments:pytools_capture'), transaction_data, secure=True)


def test_mailchimp_update(resp_token, create_or_update_client, logged_user):
    assert create_or_update_client.call_count == 0


def test_user_stay_lead(resp_token, logged_user):
    assert not has_role(logged_user, 'client')
    assert has_role(logged_user, 'lead')


def test_user_interaction_boleto(resp_token, logged_user):
    assert 'CLIENT_BOLETO' == user_facade.find_user_interactions(logged_user)[0].category


def test_redirect_url(resp_token):
    assert resp_token.json() == {
        'redirect_url': (
            '/pagamento/pytools/boleto/?'
            'boleto_barcode=1234+5678'
            '&boleto_url=https%3A%2F%2Fapi.pagar.me%2F1%2Fboletos%2Flive_cjw86db172bld2p3en7gy50l6'
        )
    }


@pytest.fixture
def resp_show_boleto(client_with_lead, logged_user):
    url = reverse('payments:pytools_boleto')
    return client_with_lead.get(
        url,
        {
            'boleto_url': 'https://api.pagar.me/1/boletos/live_cjw86db172bld2p3en7gy50l6',
            'boleto_barcode': '1234 5678',
        },
        secure=True
    )


def test_show_boleto_status_code(resp_show_boleto):
    assert resp_show_boleto.status_code == 200


@pytest.mark.parametrize(
    'content',
    [
        '1234 5678',  # Barcode
        'https://api.pagar.me/1/boletos/live_cjw86db172bld2p3en7gy50l6'
    ]
)
def test_boleto_url(resp_show_boleto, content):
    dj_assert_contains(resp_show_boleto, content)


def test_user_creation(resp_token_with_no_user, django_user_model):
    user = django_user_model.objects.get(email=CUSTOMER_EMAIL)
    assert has_role(user, 'lead')
    assert not has_role(user, 'client')


def test_user_name(resp_token_with_no_user, django_user_model):
    user = django_user_model.objects.get(email=CUSTOMER_EMAIL)
    assert user.first_name == CUSTOMER_FIRST_NAME


def test_client_update_on_mail_chimp(resp_token_with_no_user, django_user_model, create_or_update_client):
    assert create_or_update_client.call_count == 0


def test_client_lead_not_created_on_mailchimp(resp_token_with_no_user, django_user_model, create_or_update_lead):
    create_or_update_lead.assert_called_once_with(CUSTOMER_FIRST_NAME, CUSTOMER_EMAIL)


@pytest.fixture
def resp_existing_user_not_logged(db, client, create_or_update_client, create_or_update_lead, resps_success,
                                  django_user_model):
    mommy.make(django_user_model, email=CUSTOMER_EMAIL)
    return client.post(reverse('payments:pytools_capture'), transaction_data, secure=True)


def test_existing_user_not_created(resp_existing_user_not_logged, django_user_model):
    assert 1 == django_user_model.objects.all().count()
