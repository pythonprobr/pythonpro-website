import base64
import binascii
import hashlib
import hmac
from logging import Logger
from urllib import parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.defaults import bad_request

logger = Logger(__file__)


class InvalidSOOPayload(Exception):
    pass


_key_bytes = settings.DISCOURSE_SSO_SECRET.encode('utf-8')


@login_required
def sso(request):
    """
    Proceed login into discourse

    Code based on https://meta.discourse.org/t/sso-example-for-django/14258
    """
    payload = request.GET.get('sso')
    signature = request.GET.get('sig')
    try:
        decoded = _decode_payload(payload, signature)
        _check_nonce_is_present(decoded)
    except InvalidSOOPayload as e:
        return bad_request(request, e)
    else:
        nonce = parse.parse_qs(decoded)['nonce'][0]
        user = request.user
        url = _generate_discourse_login_url(nonce, user)
        return HttpResponseRedirect(url)


def _generate_discourse_login_url(nonce, user):
    params = {
        'nonce': nonce,
        'email': user.email,
        'external_id': user.id,
        'require_activation': 'false'
    }
    return_payload = base64.encodebytes(parse.urlencode(params).encode('utf-8'))
    h = hmac.new(_key_bytes, return_payload, digestmod=hashlib.sha256)
    query_string = parse.urlencode({'sso': return_payload, 'sig': h.hexdigest()})
    url = f'{settings.DISCOURSE_BASE_URL}/session/sso_login'
    url = f'{url}?{query_string}'
    return url


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
