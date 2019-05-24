import base64
import hashlib
import hmac
from random import randint
from urllib import parse

import pytest
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from rolepermissions.roles import assign_role

from pythonpro.discourse.views import _decode_payload
from pythonpro.django_assertions import dj_assert_template_used


@pytest.fixture
def nonce():
    return str(randint(-100000, 100000))


@pytest.fixture
def payload(nonce):
    return parse.urlencode({'nonce': nonce})


@pytest.fixture
def discourse_logged_user(django_user_model, fake):
    profile = fake.profile()
    user = django_user_model(email=profile['mail'], first_name=profile['name'])
    user.set_password('password')
    user.save()
    user.plain_password = 'password'
    assign_role(user, 'member')
    return user


@pytest.fixture
def client_with_member(client, discourse_logged_user):
    client.login(username=discourse_logged_user.email, password=discourse_logged_user.plain_password)
    return client


@pytest.fixture
def response(client_with_member, payload, sig=None):
    return _resp(client_with_member, payload, sig)


def _resp(client_with_member, payload, sig=None):
    encoded_payload = base64.encodebytes(payload.encode('utf-8'))
    hmac_obj = hmac.new(settings.DISCOURSE_SSO_SECRET.encode('utf-8'), encoded_payload, digestmod=hashlib.sha256)
    sig = hmac_obj.hexdigest() if sig is None else sig
    return client_with_member.get(reverse('discourse:sso'),
                                  data={'sso': encoded_payload, 'sig': sig}, secure=True)


@pytest.fixture
def response_with_wrong_sig(client_with_member, payload):
    return _resp(client_with_member, payload, 'wrong sinature')


@pytest.fixture
def response_without_nonce(client_with_member):
    return _resp(client_with_member, '')


def _extract_from_payload(response):
    qs = parse.urlparse(response.url).query
    parsed_qs = parse.parse_qs(qs)
    payload = parsed_qs['sso'][0]
    quoted = _decode_payload(payload, parsed_qs['sig'][0])
    parsed_payload = parse.parse_qs(parse.unquote(quoted))
    return {key: value[0] for key, value in parsed_payload.items()}


def test_status(response):
    assert response.status_code == 302


def test_redirect_base_url(response: HttpResponseRedirect):
    assert response.url.startswith(settings.DISCOURSE_BASE_URL)


def test_redirect_payload_has_nonce(nonce, response: HttpResponseRedirect):
    dct = _extract_from_payload(response)
    assert nonce == dct['nonce']


def test_redirect_payload_user_data(discourse_logged_user, nonce, response: HttpResponseRedirect):
    dct = _extract_from_payload(response)
    assert {
               'nonce': nonce,
               'email': discourse_logged_user.email,
               'external_id': str(discourse_logged_user.id),
               'require_activation': 'false'
           } == dct


@pytest.mark.parametrize(
    'invalid_data',
    [
        {},
        {'sso': 'sso only'},
        {'sig': 'sig only'},
        {'sig': 'invalid sig', 'sso': 'invalid sso'},
    ]
)
def test_status_invalid_data(client_with_member, invalid_data):
    response = client_with_member.get(reverse('discourse:sso'), data=invalid_data)
    return response.status_code == 400


def test_payload_without_nonce(response_without_nonce):
    return response_without_nonce.status_code == 400


def test_payload_with_mismatch_signature(response_with_wrong_sig):
    return response_with_wrong_sig.status_code == 400


def test_user_not_logged_status_code(client):
    response = client.get(reverse('discourse:sso'))
    assert response.status_code == 302


def test_user_not_logged(client):
    discourse_path = reverse('discourse:sso')
    response = client.get(discourse_path, secure=True)
    login_path = reverse('login')
    assert response.url == f'{login_path}?next={discourse_path}'


def test_lead_not_able_to_access_forum(client_with_lead,  mocker, logged_user):
    tag_as = mocker.patch('pythonpro.discourse.views.tag_as')
    discourse_path = reverse('discourse:sso')
    response = client_with_lead.get(discourse_path, secure=True)
    dj_assert_template_used(response, 'discourse/landing_page.html')
    tag_as.assert_called_once_with(logged_user.email, 'potencial-member')


def test_client_not_able_to_access_forum(client_with_client, mocker, logged_user):
    test_lead_not_able_to_access_forum(client_with_client, mocker, logged_user)
