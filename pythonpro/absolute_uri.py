from django.conf import settings


def build_absolute_uri(path: str) -> str:
    """
    Calculate absolute url by extraction first domain from settings.ALLOWED_HOSTS
    :param path: string with path
    :return: path concatenated with domain
    """
    first_host = settings.ALLOWED_HOSTS[0]
    return f'{first_host}{path}'
