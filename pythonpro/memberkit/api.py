"""
Wrapper of Memberkit api.

See doc: https://gist.github.com/rainerborene/26bc6b66bbc5dd4f78a1141df31ef718
"""
from datetime import date

import requests
from decorator import decorator
from django.conf import settings


class _ApiKeyNone:
    pass


_base_url = 'https://memberkit.com.br'
_default_api_key = _ApiKeyNone


def set_default_api_key(key: str) -> None:
    global _default_api_key
    if key:
        _default_api_key = key


set_default_api_key(settings.MEMBERKIT_API_KEY)


class MemberkitApiKeyError(Exception):
    pass


@decorator
def _configure_api_key(func, *args, api_key=_ApiKeyNone, **kwargs):
    if not settings.MEMBERKIT_ON:
        return []
    if api_key is _ApiKeyNone:
        api_key = _default_api_key
    if api_key is _ApiKeyNone:
        raise MemberkitApiKeyError('api_key must be passed as parameter or set_default_api_key if valid key')
    return func(*args, api_key=api_key, **kwargs)


@_configure_api_key
def list_membership_levels(*, api_key=_ApiKeyNone):
    response = requests.get(f'{_base_url}/api/v1/membership_levels?api_key={api_key}')
    return response.json()


@_configure_api_key
def user_detail(email, *, api_key=_ApiKeyNone):
    response = requests.get(f'{_base_url}/api/v1/users/{email}?api_key={api_key}')
    return response.json()


@_configure_api_key
def activate_user(full_name: str, email: str, subscription_type_id: int, expires_at: date = None, *,
                  api_key=_ApiKeyNone):
    if expires_at is None:
        expires_at = date(2200, 1, 1)
    data = {
        'full_name': full_name,
        'email': email,
        'status': 'active',
        'blocked': False,
        'membership_level_id': subscription_type_id,
        'unlimited': False,
        'expires_at': expires_at.strftime('%d/%m/%Y'),
    }
    requests.post(f'{_base_url}/api/v1/users?api_key={api_key}', json=data)
    return user_detail(email)
