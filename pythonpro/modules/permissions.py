from rolepermissions.permissions import register_object_checker

from pythonpro.modules.models import Content


@register_object_checker()
def access_content(role, user, content: Content) -> bool:
    module_slug = content.module_slug()
    return module_slug == 'python-birds'
