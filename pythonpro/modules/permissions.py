from rolepermissions.checkers import has_permission
from rolepermissions.permissions import register_object_checker

from pythonpro.core.roles import (
    Member,
    watch_client_modules,
    watch_lead_modules,
    watch_webdev_modules, watch_bootcamp_modules, watch_pythonista_modules
)
from pythonpro.modules.models import Content

_LEAD_MODULES = {'python-birds'}
_CLIENT_MODULES = {'python-birds', 'pytools'}
_WEBDEV_MODULES = {'python-birds', 'pytools', 'django', 'entrevistas-tecnicas'}
_BOOTCAMPER_MODULES = {
    'python-birds',
    'pytools',
    'django',
    'entrevistas-tecnicas',
    'objetos-pythonicos',
    'python-para-pythonistas',
    'python-patterns'
}
_PYTHONISTA_MODULES = {'python-birds', 'objetos-pythonicos', 'python-para-pythonistas', 'python-patterns'}


@register_object_checker()
def access_content(role, user, content: Content) -> bool:
    if role == Member:
        return True
    module_slug = content.module_slug()
    if module_slug in _BOOTCAMPER_MODULES and has_permission(user, watch_bootcamp_modules):
        return True
    if module_slug in _WEBDEV_MODULES and has_permission(user, watch_webdev_modules):
        return True
    if module_slug in _PYTHONISTA_MODULES and has_permission(user, watch_pythonista_modules):
        return True
    if module_slug in _CLIENT_MODULES and has_permission(user, watch_client_modules):
        return True
    if module_slug in _LEAD_MODULES and has_permission(user, watch_lead_modules):
        return True

    return False
