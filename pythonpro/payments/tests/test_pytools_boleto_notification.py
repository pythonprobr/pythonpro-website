import binascii
import hmac
from hashlib import sha1

import pytest
import responses
from django.conf import settings
from django.urls import reverse
from model_mommy import mommy
from rolepermissions.checkers import has_role

from pythonpro.payments.facade import PYTOOLS_PRICE, PagarmeValidationException


@pytest.fixture(scope='session')
def valid_signature():
    hashed = hmac.new(settings.PAGARME_API_KEY.encode(), valid_raw_post.encode('utf8'), sha1)
    hex_signature = binascii.b2a_hex(hashed.digest())
    return hex_signature.decode()


@pytest.fixture
def create_or_update_client(client_with_lead, logged_user, mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.create_or_update_client')


@pytest.fixture
def valid_resp(client, logged_user, valid_signature, transaction_response, create_or_update_client, mailoutbox,
               remove_tags_mock):
    transaction_response['items'][0]['id'] = f'pytools-{logged_user.id}'
    with responses.RequestsMock(assert_all_requests_are_fired=True) as r:
        r.add(r.GET, 'https://api.pagar.me/1/transactions/1396639', json=transaction_response, status=200)
        yield _generate_response(client, logged_user, valid_signature, valid_raw_post)


def _generate_response(client, user, valid_signature, raw_post):
    return client.generic(
        'POST',
        reverse('payments:pagarme_notification', kwargs={'user_id': user.id}),
        raw_post,
        secure=True,
        content_type='application/x-www-form-urlencoded',
        HTTP_X_HUB_SIGNATURE=valid_signature
    )


@pytest.fixture
def anonymous_user(db, django_user_model):
    return mommy.make(django_user_model, email=CUSTOMER_EMAIL)


@pytest.fixture
def remove_tags_mock(mocker):
    return mocker.patch('pythonpro.domain.user_facade._email_marketing_facade.remove_tags')


@pytest.fixture
def valid_resp_anonymous(client, anonymous_user, valid_signature, transaction_response, create_or_update_client,
                         mailoutbox, remove_tags_mock):
    transaction_response['items'][0]['id'] = 'pytools-'
    with responses.RequestsMock(assert_all_requests_are_fired=True) as r:
        r.add(r.GET, 'https://api.pagar.me/1/transactions/1396639', json=transaction_response, status=200)
        yield client.generic(
            'POST',
            reverse('payments:pagarme_anonymous_notification'),
            valid_raw_post,
            secure=True,
            content_type='application/x-www-form-urlencoded',
            HTTP_X_HUB_SIGNATURE=valid_signature
        )


@pytest.fixture(autouse=True)
def sync_user(mocker):
    return mocker.patch('pythonpro.domain.user_facade._discourse_facade.sync_user')


def test_user_discourse_sync_no_user(valid_resp_anonymous, django_user_model, sync_user):
    user = django_user_model.objects.first()
    sync_user.assert_called_once_with(user)


def test_anonymous_user_promoted_to_client(valid_resp_anonymous, anonymous_user):
    assert has_role(anonymous_user, 'client')
    assert not has_role(anonymous_user, 'lead')
    assert not has_role(anonymous_user, 'member')


def test_anonymous_user_tag_removed(valid_resp_anonymous, anonymous_user, remove_tags_mock):
    remove_tags_mock.assert_called_once_with(anonymous_user.email, anonymous_user.id, 'client-boleto')


def test_user_tag_removed(valid_resp, logged_user, remove_tags_mock):
    remove_tags_mock.assert_called_once_with(logged_user.email, logged_user.id, 'client-boleto')


def test_user_promoted_to_client(valid_resp, logged_user):
    assert has_role(logged_user, 'client')
    assert not has_role(logged_user, 'lead')
    assert not has_role(logged_user, 'member')


def test_promoted_to_client_on_email_marketing(valid_resp, create_or_update_client, logged_user):
    create_or_update_client.assert_called_once_with(logged_user.first_name, logged_user.email, id=logged_user.id)


def test_email_sent(valid_resp, mailoutbox, logged_user):
    sent_email = mailoutbox[0]
    assert logged_user.email in sent_email.to
    assert reverse('payments:pytools_thanks') in sent_email.body


def test_tampered_post(client, logged_user, valid_signature, transaction_response, create_or_update_client, mailoutbox):
    tampered_raw_post = valid_raw_post + 'a'
    with pytest.raises(PagarmeValidationException):
        _generate_response(client, logged_user, valid_signature, tampered_raw_post)
    assert_no_action_taken(create_or_update_client, logged_user, mailoutbox)


def assert_no_action_taken(create_or_update_client, logged_user, mailoutbox):
    assert create_or_update_client.call_count == 0
    assert len(mailoutbox) == 0
    assert has_role(logged_user, 'lead')
    assert not has_role(logged_user, 'client')


def test_item_id(client, logged_user, valid_signature, transaction_response, create_or_update_client, mailoutbox):
    transaction_response['items'][0]['id'] = f'pytools-{logged_user.id + 1}'
    with pytest.raises(PagarmeValidationException), responses.RequestsMock(assert_all_requests_are_fired=True) as r:
        r.add(r.GET, 'https://api.pagar.me/1/transactions/1396639', json=transaction_response, status=200)
        _generate_response(client, logged_user, valid_signature, valid_raw_post)

    assert_no_action_taken(create_or_update_client, logged_user, mailoutbox)


def test_no_subscription_handling(client, logged_user, valid_signature, transaction_response, create_or_update_client,
                                  mailoutbox, mocker):
    mocker.patch('pythonpro.payments.facade._pagarme.postback.validate').return_value = True
    _generate_response(
        client,
        logged_user,
        valid_signature,
        template.format(price=PYTOOLS_PRICE, object='subscription', current_status='paid'))
    assert_no_action_taken(create_or_update_client, logged_user, mailoutbox)


def test_no_handling_for_unpaid(client, logged_user, valid_signature, transaction_response, create_or_update_client,
                                mailoutbox, mocker):
    mocker.patch('pythonpro.payments.facade._pagarme.postback.validate').return_value = True
    _generate_response(
        client,
        logged_user,
        valid_signature,
        template.format(price=PYTOOLS_PRICE, object='subscription', current_status='waiting_paiment'))
    assert_no_action_taken(create_or_update_client, logged_user, mailoutbox)


template = (  # See https://docs.pagar.me/docs/gerenciando-postbacks
    'id=1396639&'
    'fingerprint=ca22ed4f65a29365fd17eec4366b1c7f72ed8383&'
    'event=transaction_status_changed&'
    'old_status=processing&'
    'desired_status=paid&'
    'current_status={current_status}&'
    'object={object}&'
    'transaction%5Bobject%5D=transaction&'
    'transaction%5Bstatus%5D=paid&'
    'transaction%5Brefuse_reason%5D=&'
    'transaction%5Bstatus_reason%5D=acquirer&'
    'transaction%5Bacquirer_response_code%5D=0000&'
    'transaction%5Bacquirer_name%5D=pagarme&'
    'transaction%5Bacquirer_id%5D=57fc00c44fe346091113627a&'
    'transaction%5Bauthorization_code%5D=531866&'
    'transaction%5Bsoft_descriptor%5D=&'
    'transaction%5Btid%5D=1396639&'
    'transaction%5Bnsu%5D=1396639&'
    'transaction%5Bdate_created%5D=2017-03-27T18%3A02%3A49.449Z&'
    'transaction%5Bdate_updated%5D=2017-03-27T18%3A02%3A49.839Z&'
    'transaction%5Bamount%5D=1000&'
    'transaction%5Bauthorized_amount%5D={price}&'
    'transaction%5Bpaid_amount%5D=1000&'
    'transaction%5Brefunded_amount%5D=0&'
    'transaction%5Binstallments%5D=1&'
    'transaction%5Bid%5D=1396639&'
    'transaction%5Bcost%5D=50&'
    'transaction%5Bcard_holder_name%5D=sadasd&'
    'transaction%5Bcard_last_digits%5D=4242&'
    'transaction%5Bcard_first_digits%5D=424242&'
    'transaction%5Bcard_brand%5D=visa&'
    'transaction%5Bcard_pin_mode%5D=&'
    'transaction%5Bpostback_url%5D=http%3A%2F%2Frequestb.in%2F18fa7xq1&'
    'transaction%5Bpayment_method%5D=credit_card&'
    'transaction%5Bcapture_method%5D=ecommerce&'
    'transaction%5Bantifraud_score%5D=&'
    'transaction%5Bboleto_url%5D=&'
    'transaction%5Bboleto_barcode%5D=&'
    'transaction%5Bboleto_expiration_date%5D=&'
    'transaction%5Breferer%5D=api_key&'
    'transaction%5Bip%5D=187.11.121.49&'
    'transaction%5Bsubscription_id%5D=&'
    'transaction%5Bphone%5D%5Bobject%5D=phone&'
    'transaction%5Bphone%5D%5Bddi%5D=55&'
    'transaction%5Bphone%5D%5Bddd%5D=47&'
    'transaction%5Bphone%5D%5Bnumber%5D=992739596&'
    'transaction%5Bphone%5D%5Bid%5D=87699&'
    'transaction%5Baddress%5D%5Bobject%5D=address&'
    'transaction%5Baddress%5D%5Bstreet%5D=Avenida%20Atl%C3%A2ntica&'
    'transaction%5Baddress%5D%5Bcomplementary%5D=ZApto.%201701&'
    'transaction%5Baddress%5D%5Bstreet_number%5D=4330&'
    'transaction%5Baddress%5D%5Bneighborhood%5D=Centro&'
    'transaction%5Baddress%5D%5Bcity%5D=Balne%C3%A1rio%20Cambori%C3%BA&'
    'transaction%5Baddress%5D%5Bstate%5D=SC&'
    'transaction%5Baddress%5D%5Bzipcode%5D=88330027&'
    'transaction%5Baddress%5D%5Bcountry%5D=Brasil&'
    'transaction%5Baddress%5D%5Bid%5D=90140&'
    'transaction%5Bcustomer%5D%5Bobject%5D=customer&'
    'transaction%5Bcustomer%5D%5Bdocument_number%5D=91525464205&'
    'transaction%5Bcustomer%5D%5Bdocument_type%5D=cpf&'
    'transaction%5Bcustomer%5D%5Bname%5D=Henrique%20Foletto&'
    'transaction%5Bcustomer%5D%5Bemail%5D=cliente.silve%40gmail.com&'
    'transaction%5Bcustomer%5D%5Bborn_at%5D=2017-02-21T02%3A00%3A00.000Z&'
    'transaction%5Bcustomer%5D%5Bgender%5D=&'
    'transaction%5Bcustomer%5D%5Bdate_created%5D=2017-02-07T13%3A04%3A13.151Z&'
    'transaction%5Bcustomer%5D%5Bid%5D=147714&'
    'transaction%5Bcard%5D%5Bobject%5D=card&'
    'transaction%5Bcard%5D%5Bid%5D=card_cizfjqn8n001nkx6dhisnhrz9&'
    'transaction%5Bcard%5D%5Bdate_created%5D=2017-02-21T13%3A08%3A04.010Z&'
    'transaction%5Bcard%5D%5Bdate_updated%5D=2017-02-21T13%3A08%3A04.469Z&'
    'transaction%5Bcard%5D%5Bbrand%5D=visa&'
    'transaction%5Bcard%5D%5Bholder_name%5D=sadasd&'
    'transaction%5Bcard%5D%5Bfirst_digits%5D=424242&'
    'transaction%5Bcard%5D%5Blast_digits%5D=4242&'
    'transaction%5Bcard%5D%5Bcountry%5D=US&'
    'transaction%5Bcard%5D%5Bfingerprint%5D=f22mP%2Bw98PvO&'
    'transaction%5Bcard%5D%5Bvalid%5D=true&'
    'transaction%5Bcard%5D%5Bexpiration_date%5D=0119&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Bobject%5D=split_rule&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Bid%5D=sr_cj0sf8o3j00s2n66evsfbcm4u&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Brecipient_id%5D=re_ciu4jif1j007td56dsm17yew9&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Bcharge_processing_fee%5D=true&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Bcharge_remainder%5D=true&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Bliable%5D=true&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Bpercentage%5D=100&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Bamount%5D=&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Bdate_created%5D=2017-03-27T18%3A02%3A49.471Z&'
    'transaction%5Bsplit_rules%5D%5B0%5D%5Bdate_updated%5D=2017-03-27T18%3A02%3A49.471Z&'
    'transaction%5Bmetadata%5D%5BidProduto%5D=teste'
)
valid_raw_post = template.format(price=PYTOOLS_PRICE, object='transaction', current_status='paid')

CUSTOMER_EMAIL = 'foo@bar.com'


@pytest.fixture
def transaction_response():
    return {
        'object': 'transaction', 'status': 'waiting_payment', 'refuse_reason': None, 'status_reason': 'acquirer',
        'acquirer_response_code': None, 'acquirer_name': 'pagarme', 'acquirer_id': '5cdec7071458b442125d940b',
        'authorization_code': None, 'soft_descriptor': None, 'tid': 6416381, 'nsu': 6416381,
        'date_created': '2019-05-28T21:31:38.391Z', 'date_updated': '2019-05-28T21:31:40.601Z', 'amount': PYTOOLS_PRICE,
        'authorized_amount': PYTOOLS_PRICE, 'paid_amount': 0, 'refunded_amount': 0, 'installments': 1, 'id': 1396639,
        'cost': 0,
        'card_holder_name': None, 'card_last_digits': None, 'card_first_digits': None, 'card_brand': None,
        'card_pin_mode': None, 'card_magstripe_fallback': False,
        'postback_url': 'http://localhost:8000/pagamento/pargarme/notificacao/6', 'payment_method': 'boleto',
        'capture_method': 'ecommerce', 'antifraud_score': None, 'boleto_url': 'https://pagar.me',
        'boleto_barcode': '1234 5678', 'boleto_expiration_date': '2019-06-04T03:00:00.000Z',
        'referer': 'encryption_key', 'ip': '201.75.170.145', 'subscription_id': None, 'phone': None, 'address': None,
        'customer': {
            'object': 'customer', 'id': 2088581, 'external_id': CUSTOMER_EMAIL, 'type': 'corporation', 'country': 'br',
            'document_number': None, 'document_type': 'cpf', 'name': 'Daen', 'email': CUSTOMER_EMAIL,
            'phone_numbers': ['+5512997411854'], 'born_at': None, 'birthday': None, 'gender': None,
            'date_created': '2019-05-28T21:31:38.355Z', 'documents': [{
                'object': 'document',
                'id': 'doc_cjw8bfvgc0a0us86ekrfo4b3y',
                'type': 'cnpj', 'number': '18152564000105'
            }]
        }, 'billing': {
            'object': 'billing', 'id': 996136, 'name': 'Daen', 'address': {
                'object': 'address', 'street': 'Rua Doutor Geraldo Campos Moreira', 'complementary': 'Sem complemento',
                'street_number': '676', 'neighborhood': 'Cidade Monções', 'city': 'São Paulo', 'state': 'SP',
                'zipcode': '04571020', 'country': 'br', 'id': 2281755
            }
        }, 'shipping': None, 'items': [{
            'object': 'item', 'id': 'pytools-2', 'title': 'Curso PyTools',
            'unit_price': PYTOOLS_PRICE, 'quantity': 1, 'category': None, 'tangible': False,
            'venue': None, 'date': None
        }], 'card': None, 'split_rules': None, 'metadata': {}, 'antifraud_metadata': {},
        'reference_key': None, 'device': None, 'local_transaction_id': None, 'local_time': None, 'fraud_covered': False,
        'order_id': None, 'risk_level': 'unknown', 'receipt_url': None, 'payment': None, 'addition': None,
        'discount': None
    }
