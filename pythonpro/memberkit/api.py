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
