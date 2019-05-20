import json

import pytest
import responses

from pythonpro.mailchimp import facade

roles_to_ids = {facade._LEAD: 'lead_id', facade._CLIENT: 'client_id', facade._MEMBER: 'member_id'}

member_url = 'https://us17.api.mailchimp.com/3.0/lists/list_id/members/f21127224363bab9ff7af3574549a203'

categories_url = 'https://us17.api.mailchimp.com/3.0/lists/list_id/interest-categories'
interests_url = 'https://us17.api.mailchimp.com/3.0/lists/list_id/interest-categories/ac597f0bb2/interests'


@pytest.fixture
def resps():
    facade._list_id = 'list_id'
    with responses.RequestsMock(assert_all_requests_are_fired=False) as r:
        r.add(r.GET, categories_url, json=categories_response, status=200)
        r.add(r.GET, interests_url, json=interests_response, status=200)
        yield r


def test_creation(existing_lead, resps):
    resps.add(
        resps.GET,
        member_url,
        json={
            'type': 'http://developer.mailchimp.com/documentation/mailchimp/guides/error-glossary/',
            'title': 'Resource Not Found',
            'status': 404,
            'detail': 'The requested resource could not be found.',
            'instance': 'b2b05bea-464c-4774-ab7b-40ae9466fb03'
        },
        status=404)
    resps.add(resps.POST, 'https://us17.api.mailchimp.com/3.0/lists/list_id/members', json=existing_lead, status=200)
    expected_on_request = {
        'email_address': 'host@python.pro.br',
        'status': 'subscribed',
        'merge_fields': {
            "FNAME": 'Renzo',
        },
        'interests': {
            roles_to_ids[facade._LEAD]: True
        }
    }
    facade.create_or_update_lead('Renzo', 'host@python.pro.br')
    assert json.loads(resps.calls[-1].request.body) == expected_on_request


def test_update_user_no_role(existing_lead, resps):
    for id_ in roles_to_ids.values():
        existing_lead['interests'][id_] = False
    resps.add(resps.GET, member_url, json=existing_lead, status=200)
    resps.add(resps.PATCH, member_url, json=existing_lead, status=200)
    interests = facade.create_or_update_lead('Renzo', 'host@python.pro.br')['interests']
    assert_member_roles(expected_lead=True, expected_client=False, expected_member=False, interests=interests)


def test_update_already_lead(existing_lead, resps):
    for id_ in roles_to_ids.values():
        existing_lead['interests'][id_] = False
    existing_lead['interests'][roles_to_ids[facade._LEAD]] = True
    resps.add(resps.GET, member_url, json=existing_lead, status=200)
    resps.add(resps.PATCH, member_url, json=existing_lead, status=200)
    interests = facade.create_or_update_lead('Renzo', 'host@python.pro.br')['interests']
    assert_member_roles(expected_lead=True, expected_client=False, expected_member=False, interests=interests)


def test_update_no_client_downgrade(existing_lead, resps):
    for id_ in roles_to_ids.values():
        existing_lead['interests'][id_] = False
    existing_lead['interests'][roles_to_ids[facade._CLIENT]] = True
    resps.add(resps.GET, member_url, json=existing_lead, status=200)
    resps.add(resps.PATCH, member_url, json=existing_lead, status=200)
    interests = facade.create_or_update_lead('Renzo', 'host@python.pro.br')['interests']
    assert_member_roles(expected_lead=False, expected_client=True, expected_member=False, interests=interests)


def test_update_no_member_downgrade(existing_lead, resps):
    for id_ in roles_to_ids.values():
        existing_lead['interests'][id_] = False
    existing_lead['interests'][roles_to_ids[facade._MEMBER]] = True
    resps.add(resps.GET, member_url, json=existing_lead, status=200)
    resps.add(resps.PATCH, member_url, json=existing_lead, status=200)
    interests = facade.create_or_update_lead('Renzo', 'host@python.pro.br')['interests']
    assert_member_roles(expected_lead=False, expected_client=False, expected_member=True, interests=interests)


def assert_member_roles(expected_lead, expected_client, expected_member, interests):
    assert (expected_lead, expected_client, expected_member) == tuple(interests[id_] for id_ in roles_to_ids.values())


interests_response = {
    'interests': [{
        'category_id': 'ac597f0bb2',
        'list_id': 'list_id',
        'id': 'lead_id',
        'name': 'Lead',

    },
        {
            'category_id': 'ac597f0bb2',
            'list_id': 'list_id',
            'id': 'client_id',
            'name': 'Client',

        },
        {
            'category_id': 'ac597f0bb2',
            'list_id': 'list_id',
            'id': 'member_id',
            'name': 'Member',

        }],
    'list_id': 'list_id',
    'category_id': 'ac597f0bb2',
}

categories_response = {
    'list_id': 'list_id',
    'categories': [{
        'list_id': 'list_id',
        'id': 'ac597f0bb2',
        'title': 'Role',

    }]
}


@pytest.fixture
def existing_lead():
    return {
        'id': 'f21127224363bab9ff7af3574549a203',
        'email_address': 'host@python.pro.br',
        'unique_email_id': 'cd83788550',
        'web_id': 79949355,
        'email_type': 'html',
        'status': 'subscribed',
        'merge_fields': {'FNAME': 'Foo'},
        'interests': {'lead_id': True, 'client_id': False, 'member_id': False},
        'stats': {'avg_open_rate': 0, 'avg_click_rate': 0},
        'ip_signup': '',
        'timestamp_signup': '',
        'ip_opt': '179.234.54.51',
        'timestamp_opt': '2019-05-20T13:26:35+00:00',
        'member_rating': 2,
        'last_changed': '2019-05-20T13:26:35+00:00',
        'language': 'pt',
        'vip': False,
        'list_id': 'list_id',

    }
