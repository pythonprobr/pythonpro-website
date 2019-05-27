import pagarme as _pagarme
from django.conf import settings

_pagarme.authentication_key(settings.PAGARME_API_KEY)
PYTOOLS_PRICE = 9999


def pytools_capture(token: str):
    return _pagarme.transaction.capture(token, {'amount': PYTOOLS_PRICE})
