from functools import lru_cache

from activecampaign.client import Client
from activecampaign.exception import ActiveCampaignError
from django.conf import settings

_client = Client(settings.ACTIVE_CAMPAIGN_URL, settings.ACTIVE_CAMPAIGN_KEY)
_roles_cache = None
_LEAD = 'lead'
_CLIENT = 'client'
_MEMBER = 'member'

_ROLES = {_LEAD, _CLIENT, _MEMBER}


def create_or_update_with_no_role(name: str, email: str, *tags, id='0'):
    return _create_or_update(name, email, '', *tags, id=id)


def create_or_update_lead(name: str, email: str, *tags, id='0'):
    return _create_or_update(name, email, _LEAD, *tags, id=id)


def create_or_update_client(name: str, email: str, *tags, id='0'):
    return _create_or_update(name, email, _CLIENT, *tags, id=id)


def create_or_update_member(name: str, email: str, *tags, id='0'):
    return _create_or_update(name, email, _MEMBER, *tags, id=id)


def _create_or_update(name: str, email: str, role: str, *tags, id='0'):
    prospect_list_id = _get_lists()['Prospects']
    id = str(id)
    tags = list(tags)

    data = {
        'email': email,
        'first_name': name.split()[0],
        'tags': ','.join(tags),
        'field[%PYTHONPRO_ID%]': id,
        f'p[{prospect_list_id}]': prospect_list_id,
        'status': '1',
    }
    if id == '0':
        contact = _client.contacts.create_contact(data)
    else:
        try:
            contacts = _client.contacts.list({'filters[fields][%PYTHONPRO_ID%]': id})
        except ActiveCampaignError:
            contact = _client.contacts.create_contact(data)
        else:
            data['id'] = contacts['0']['id']
            contact = _client.contacts.edit_contact(data)
    if role:
        grant_role(email, id, role)
    return contact


def _find_active_campaign_contact_id(id):
    raise ActiveCampaignError()
    id = str(id)
    contacts_list = _client.contacts.list({'filters[fields][%PYTHONPRO_ID%]': id})
    return contacts_list['0']['id']


def grant_role(email, id, role: str):
    role = role.lower()
    if role not in _ROLES:
        raise ValueError(f'Role {role} must be one of {_ROLES}')

    roles_to_remove = set(_ROLES)
    roles_to_remove.remove(role)
    role_to_grant = role.capitalize()
    roles_to_remove = map(str.capitalize, roles_to_remove)

    try:
        user_data = {'id': _find_active_campaign_contact_id(id)}
    except ActiveCampaignError:
        user_data = {'email': email}
    role_to_grant_data = _build_tags_array([role_to_grant])
    role_to_grant_data.update(user_data)
    _client.contacts.add_tag(role_to_grant_data)

    roles_to_remove_data = _build_tags_array([roles_to_remove])
    roles_to_remove_data.update(user_data)
    _client.contacts.remove_tag(roles_to_remove_data)


def tag_as(email: str, id: int, *tags):
    data = _build_tags_array(tags)
    try:
        data['id'] = _find_active_campaign_contact_id(id)
    except ActiveCampaignError:
        data['email'] = email
    return _client.contacts.add_tag(data)


def _build_tags_array(tags) -> dict:
    """
    Check https://community.activecampaign.com/t/api-add-multiple-tags/3592/3
    """
    return {f'tags[{i}]': tag for i, tag in enumerate(tags, start=1)}


def remove_tags(email: str, id: int, *tags):
    data = _build_tags_array(tags)
    try:
        data['id'] = _find_active_campaign_contact_id(id)
    except ActiveCampaignError:
        data['email'] = email
    return _client.contacts.remove_tag(data)


@lru_cache(maxsize=1)
def _get_lists():
    """
    Return dict of existing lists with name: id items
    """
    dct = _client.lists.get_lists()

    return {list_item['name']: list_item['id'] for k, list_item in dct.items() if k.isdigit()}


if __name__ == '__main__':
    # client = create_or_update_lead('Renzo Nuccitelli', 'renzo@python.pro.br', id=1)
    # client = tag_as('renzo@python.pro.br', 1, 'outro_teste')
    # print(client)
    # client = tag_as('renzo@python.pro.br', 2, 'a', 'b')
    # print(client)
    # client = remove_tags('renzo@python.pro.br', 1, 'outro_teste')
    # print(client)
    # client = remove_tags('renzo@python.pro.br', 2, 'a', 'b')
    # print(client)
    # grant_role('renzo@python.pro.br', 1, 'client')
    # grant_role('renzo@python.pro.br', 2, 'member')
    print(_find_active_campaign_contact_id(1))
