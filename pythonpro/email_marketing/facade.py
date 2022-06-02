from functools import lru_cache
from json.decoder import JSONDecodeError

from activecampaign.client import Client
from activecampaign.exception import ActiveCampaignError
from celery import shared_task
from django.conf import settings

_client = Client(settings.ACTIVE_CAMPAIGN_URL, settings.ACTIVE_CAMPAIGN_KEY)
_roles_cache = None
LEAD = 'lead'
CLIENT = 'client'
MEMBER = 'member'
WEBDEV = 'webdev'
FELLOW = 'fellow'
BOOTCAMPER = 'bootcamper'
DATA_SCIENTIST = 'data-scientist'
PYTHONISTA = 'pythonista'

_PYTHON_PRO_ROLES = {LEAD, CLIENT, WEBDEV, BOOTCAMPER, MEMBER, FELLOW}

_ALL_ROLES = set(_PYTHON_PRO_ROLES)
_ALL_ROLES.add(DATA_SCIENTIST)
_ALL_ROLES.add(PYTHONISTA)

run_until_available = shared_task(autoretry_for=(JSONDecodeError,), retry_backoff=True, max_retries=None)


@run_until_available
def create_or_update_with_no_role(name: str, email: str, *tags, id='0', phone=None, utm_source=None):
    return create_or_update_user(name, email, '', *tags, id=id, phone=phone, utm_source=utm_source)


@run_until_available
def create_or_update_lead(name: str, email: str, *tags, id='0', phone=None, utm_source=None):
    return create_or_update_user(name, email, LEAD, *tags, id=id, phone=phone, utm_source=utm_source)


@run_until_available
def create_or_update_bootcamper(name: str, email: str, *tags, id='0', phone=None):
    return create_or_update_user(name, email, BOOTCAMPER, *tags, id=id, phone=phone)


@run_until_available
def create_or_update_data_scientist(name: str, email: str, *tags, id='0', phone=None):
    return create_or_update_user(name, email, DATA_SCIENTIST, *tags, id=id, phone=phone)


@run_until_available
def create_or_update_pythonista(name: str, email: str, *tags, id='0', phone=None):
    return create_or_update_user(name, email, PYTHONISTA, *tags, id=id, phone=phone)


@run_until_available
def create_or_update_client(name: str, email: str, *tags, id='0', phone=None):
    return create_or_update_user(name, email, CLIENT, *tags, id=id, phone=phone)


@run_until_available
def create_or_update_member(name: str, email: str, *tags, id='0', phone=None):
    return create_or_update_user(name, email, MEMBER, *tags, id=id, phone=phone)


@run_until_available
def create_or_update_webdev(name: str, email: str, *tags, id='0', phone=None):
    return create_or_update_user(name, email, WEBDEV, *tags, id=id, phone=phone)


@run_until_available
def create_or_update_fellow(name: str, email: str, *tags, id='0', phone=None):
    return create_or_update_user(name, email, FELLOW, *tags, id=id, phone=phone)


def _normalise_id(id):
    """
    Need to normalize id because active campaing search for custom fields like a "startswith" method. Check:
    https://community.activecampaign.com/t/contact-api-v3-search-by-query-params-fields/5658/8?u=python

    So we have to add 0 to avoid a not exact match
    """
    if id is None:
        id = 0
    id = int(id)
    return f'{id:010d}'


@run_until_available
def create_or_update_user(name: str, email: str, role: str, *tags, id='0', phone=None, utm_source=None):
    if settings.ACTIVE_CAMPAIGN_TURNED_ON is False:
        return
    prospect_list_id = _get_lists()['Prospects']
    tags = list(tags)
    id = _normalise_id(id)

    data = {
        'email': email,
        'first_name': name.split()[0],
        'tags': ','.join(tags),
        f'p[{prospect_list_id}]': prospect_list_id,
        'status': '1',
    }
    if phone is not None:
        data['phone'] = phone
    if utm_source is not None:
        data['field[%UTM_SOURCE%]'] = utm_source
    if id == _normalise_id('0'):
        contact = _client.contacts.create_contact(data)
    else:
        data['field[%PYTHONPRO_ID%]'] = id
        try:
            contact_id = _find_active_campaign_contact_id(id)
        except ActiveCampaignError:
            contact = _client.contacts.create_contact(data)
        else:
            data['id'] = contact_id
            contact = _client.contacts.edit_contact(data)
    if role:
        grant_role(email, id, role)
    usuarios_ativos_list_id = _get_lists()['Usuários Ativos']
    _client.contacts.update_list_status(usuarios_ativos_list_id, contact['subscriber_id'], 1)
    return contact


def _find_active_campaign_contact_id(id):
    id = _normalise_id(id)
    contacts_list = _client.contacts.list({'filters[fields][%PYTHONPRO_ID%]': id, 'full': 0})
    if '1' in contacts_list:
        raise ActiveCampaignError('Should return only one field')
    return contacts_list['0']['id']


def grant_role(email, id, role: str):
    if settings.ACTIVE_CAMPAIGN_TURNED_ON is False:
        return
    role = role.lower()

    if role not in _ALL_ROLES:
        raise ValueError(f'Role {role} must be one of {_ALL_ROLES}')
    if role in {DATA_SCIENTIST, PYTHONISTA}:
        roles_to_remove = set()
        role_to_grant = role.capitalize()
    elif role in _PYTHON_PRO_ROLES:
        roles_to_remove = set(_PYTHON_PRO_ROLES)
        roles_to_remove.remove(role)
        role_to_grant = role.capitalize()
        roles_to_remove = map(str.capitalize, roles_to_remove)
    else:
        raise ValueError(f'Invalid role: {role}')

    try:
        user_data = {'id': _find_active_campaign_contact_id(id)}
    except ActiveCampaignError:
        user_data = {'email': email}
    role_to_grant_data = _build_tags_array([role_to_grant])
    role_to_grant_data.update(user_data)
    _client.contacts.add_tag(role_to_grant_data)

    if roles_to_remove:
        roles_to_remove_data = _build_tags_array(roles_to_remove)
        roles_to_remove_data.update(user_data)
        _client.contacts.remove_tag(roles_to_remove_data)


@run_until_available
def tag_as(email: str, id: int, *tags):
    if settings.ACTIVE_CAMPAIGN_TURNED_ON is False:
        return
    data = _build_tags_array(tags)
    try:
        data['id'] = _find_active_campaign_contact_id(id)
    except ActiveCampaignError:
        data['email'] = email
    else:
        # Activating users all the time she is tagged
        usuarios_ativos_list_id = _get_lists()['Usuários Ativos']
        _client.contacts.update_list_status(usuarios_ativos_list_id, data['id'], 1)
    return _client.contacts.add_tag(data)


def _build_tags_array(tags) -> dict:
    """
    Check https://community.activecampaign.com/t/api-add-multiple-tags/3592/3
    """
    return {f'tags[{i}]': tag for i, tag in enumerate(tags, start=1)}


@run_until_available
def remove_tags(email: str, id: int, *tags):
    if settings.ACTIVE_CAMPAIGN_TURNED_ON is False:
        return
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
