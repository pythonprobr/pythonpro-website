import base64
import binascii
import hashlib
import hmac
from logging import Logger
from urllib import parse

from django.conf import settings

_key_bytes = settings.DISCOURSE_SSO_SECRET.encode('utf-8')

__all__ = (
    'generate_discourse_login_url',
    'InvalidSOOPayload',
    'MissingDiscourseAPICredentials',
)


class InvalidSOOPayload(Exception):
    pass


class MissingDiscourseAPICredentials(Exception):
    pass


logger = Logger(__file__)


def generate_discourse_login_url(user, payload, signature):
    """
    Generate Discourse login url if payload matches signature
    It will raise InvalidSOOPayload otherwise
    :param user: Django's User
    :param payload: payload to be validated
    :param signature: payload signature
    :return: url to login user
    """
    decoded = _decode_payload(payload, signature)
    _check_nonce_is_present(decoded)
    nonce = parse.parse_qs(decoded)['nonce'][0]
    return _generate_discourse_login_url(nonce, user)


def _generate_discourse_login_url(nonce, user):
    params = {
        'nonce': nonce,
        'email': user.email,
        'external_id': user.id,
        'require_activation': 'false',
        'groups': ','.join(g.name for g in user.groups.all())
    }
    sso_payload, signature = generate_sso_payload_and_signature(params)
    query_string = parse.urlencode({'sso': sso_payload, 'sig': signature})
    url = f'{settings.DISCOURSE_BASE_URL}/session/sso_login'
    url = f'{url}?{query_string}'
    return url


def generate_sso_payload_and_signature(params):
    sso_payload = base64.encodebytes(parse.urlencode(params).encode('utf-8'))
    h = hmac.new(_key_bytes, sso_payload, digestmod=hashlib.sha256)
    signature = h.hexdigest()
    return sso_payload, signature


def _decode_payload(payload, signature):
    _check_mandatory_params(payload, signature)
    payload_bytes = parse.unquote(payload).encode('utf-8')
    try:
        decoded = base64.decodebytes(payload_bytes).decode('utf-8')
    except binascii.Error as e:
        msg = f'Invalid base64 payload: {payload}'
        logger.warning(msg)
        raise InvalidSOOPayload(msg) from e
    else:
        h = hmac.new(_key_bytes, payload_bytes, digestmod=hashlib.sha256)
        calculated_signature = h.hexdigest()
        _check_signature(calculated_signature, signature)
        return decoded


def _check_signature(calculated_signature, signature):
    if not hmac.compare_digest(calculated_signature, signature):
        msg = f'Signatures mismatch: {signature} != {calculated_signature}'
        logger.warning(msg)
        raise InvalidSOOPayload(msg)


def _check_nonce_is_present(decoded):
    if 'nonce' not in decoded:
        msg = f'Nonce not in payload={decoded}'
        logger.warning(msg)
        raise InvalidSOOPayload(msg)


def _check_mandatory_params(payload, signature):
    if payload is None or signature is None:
        msg = f'Invalid SSO payload={payload} signature={signature}'
        logger.warning(msg)
        raise InvalidSOOPayload(msg)
