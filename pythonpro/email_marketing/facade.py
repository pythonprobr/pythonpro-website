from django.conf import settings
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

_client = MailChimp(settings.MAILCHIMP_API_KEY)
_list_id = settings.MAILCHIMP_LIST_ID
_members_client = _client.lists.members
_segments_client = _client.lists.segments
_roles_cache = None
_LEAD = 'lead'
_CLIENT = 'client'
_MEMBER = 'member'

_ROLES = (_LEAD, _CLIENT, _MEMBER)


def create_or_update_with_no_role(name: str, email: str, *tags):
    return _create_or_update(name, email, '', *tags)


def create_or_update_lead(name: str, email: str, *tags):
    return _create_or_update(name, email, _LEAD, *tags)


def create_or_update_client(name: str, email: str, *tags):
    return _create_or_update(name, email, _CLIENT, *tags)


def create_or_update_member(name: str, email: str, *tags):
    return _create_or_update(name, email, _MEMBER, *tags)


def _create_or_update(name: str, email: str, role: str, *tags):
    try:
        return _update_member(name, email, role, *tags)
    except MailChimpError as e:
        if e.args[0]['status'] == 404:
            tags_with_never_watched = ['never-watched-video']
            tags_with_never_watched.extend(tags)

            # https://developer.mailchimp.com/documentation/mailchimp/reference/lists/members/
            data = {
                'email_address': email,
                'status': 'subscribed',
                'merge_fields': {
                    "FNAME": name,
                },
                'tags': tags_with_never_watched
            }
            roles_dct = _build_roles()
            if role in roles_dct:
                role_id = roles_dct[role]
                data['interests'] = {role_id: True}
            return _members_client.create(_list_id, data)


def tag_as(email: str, *tags):
    return _members_client.tags.update(_list_id, email, {'tags': [{'name': tag, 'status': 'active'} for tag in tags]})


def remove_tags(email: str, *tags):
    return _members_client.tags.update(_list_id, email, {'tags': [{'name': tag, 'status': 'inactive'} for tag in tags]})


def _update_member(name: str, email: str, role: str = '', *tags) -> dict:
    member = _members_client.get(_list_id, email)
    interests = member['interests']
    member['merge_fields']['FNAME'] = name
    roles_to_ids = _build_roles()
    # Assure the is now downgrade on user role
    if role == _MEMBER:
        interests[roles_to_ids[_MEMBER]] = True
        interests[roles_to_ids[_CLIENT]] = False
        interests[roles_to_ids[_LEAD]] = False
    elif role == _CLIENT and not interests[roles_to_ids[_MEMBER]]:
        interests[roles_to_ids[_MEMBER]] = False
        interests[roles_to_ids[_CLIENT]] = True
        interests[roles_to_ids[_LEAD]] = False
    elif role == _LEAD and not interests[roles_to_ids[_MEMBER]] and not interests[roles_to_ids[_CLIENT]]:
        interests[roles_to_ids[_MEMBER]] = False
        interests[roles_to_ids[_CLIENT]] = False
        interests[roles_to_ids[_LEAD]] = True
    if tags:
        tag_as(email, *tags)
    member['status'] = 'subscribed'
    _members_client.update(_list_id, email, member)
    return member


def _extract_role_category_id() -> str:
    for c in _client.lists.interest_categories.all(_list_id)['categories']:
        if c['title'].lower() == 'role':
            return c['id']


def _build_roles() -> dict:
    global _roles_cache
    if _roles_cache:
        return _roles_cache
    _roles_cache = {}
    role_category_id = _extract_role_category_id()
    for c in _client.lists.interest_categories.interests.all(_list_id, role_category_id)['interests']:
        _roles_cache[c['name'].lower()] = c['id']
    return _roles_cache


if __name__ == '__main__':
    create_or_update_with_no_role('Renzo S', 'renzo+1@python.pro.br', 'turma-bruno-rocha-semana-do-programador')
