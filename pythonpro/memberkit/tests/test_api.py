from datetime import date

import pytest
from requests import HTTPError
from responses import matchers

from pythonpro.memberkit import api


@pytest.fixture
def api_key():
    key = 'some_key'
    api.set_default_api_key(key)
    return key


@pytest.fixture(autouse=True)
def memberkit_api_on(settings):
    settings.MEMBERKIT_ON = True


def test_api_delete_success(responses, api_key):
    memberkit_user_id = 1
    responses.add(
        responses.DELETE,
        f'https://memberkit.com.br/api/v1/users/{memberkit_user_id}?api_key={api_key}',
        status=204
    )
    assert api.delete_user(memberkit_user_id).status_code == 204


def test_api_delete_user_not_found(responses, api_key):
    memberkit_user_id = 1
    responses.add(
        responses.DELETE,
        f'https://memberkit.com.br/api/v1/users/{memberkit_user_id}?api_key={api_key}',
        status=404
    )
    with pytest.raises(HTTPError):
        api.delete_user(memberkit_user_id)


def test_user_detail_success(responses, api_key):
    memberkit_user_id = 14842209
    user_json_resp = {
        'id': memberkit_user_id,
        'full_name': 'Aluno Teste',
        'email': 'aluno_teste@dev.pro.br',
        'sign_in_count': 2,
        'current_sign_in_at': '2022-12-21T11:32:28.633-03:00',
        'profile_image_url': 'https://images.memberkit.com.br/',
        'created_at': '2022-12-19T11:46:18.864-03:00',
        'updated_at': '2023-03-24T11:28:18.351-03:00',
        'bio': '',
        'unlimited': False,
        'blocked': False,
        'metadata': {},
        'enrollments': [],
        'memberships': [
            {'id': 7768186,
             'membership_level_id': 4420,
             'status': 'expired',
             'expire_date': '2023-03-24'},
            {'id': 7768133,
             'membership_level_id': 11610,
             'status': 'expired',
             'expire_date': '0121-02-21'},
            {'id': 7233514,
             'membership_level_id': 12180,
             'status': 'active',
             'expire_date': '2024-09-15'},
            {'id': 7768155,
             'membership_level_id': 16738,
             'status': 'active',
             'expire_date': '2200-01-01'}
        ]
    }

    responses.add(
        responses.GET,
        f'https://memberkit.com.br/api/v1/users/{memberkit_user_id}?api_key={api_key}',
        json=user_json_resp,
        status=200
    )
    assert user_json_resp == api.user_detail(memberkit_user_id)


def test_user_detail_not_found(responses, api_key):
    memberkit_user_id = 148422093
    json_resp = {'error': 'Not Found'}
    responses.add(
        responses.GET,
        f'https://memberkit.com.br/api/v1/users/{memberkit_user_id}?api_key={api_key}',
        json=json_resp,
        status=404
    )
    with pytest.raises(HTTPError):
        api.user_detail(memberkit_user_id)


def test_update_user_subscription(responses, api_key):
    memberkit_user_id = 14842209
    subscription_id = 16738
    full_name = 'Aluno Teste'
    email = 'aluno_teste@dev.pro.br'
    user_json_resp = {
        'id': memberkit_user_id,
        'full_name': full_name,
        'email': email,
        'sign_in_count': 2,
        'current_sign_in_at': '2022-12-21T11:32:28.633-03:00',
        'profile_image_url': 'https://images.memberkit.com.br/',
        'created_at': '2022-12-19T11:46:18.864-03:00',
        'updated_at': '2023-03-24T11:28:18.351-03:00',
        'bio': '',
        'unlimited': False,
        'blocked': False,
        'metadata': {},
        'enrollments': [],
        'memberships': [
            {'id': 7768186,
             'membership_level_id': 4420,
             'status': 'expired',
             'expire_date': '2023-03-24'},
            {'id': 7768133,
             'membership_level_id': 11610,
             'status': 'expired',
             'expire_date': '0121-02-21'},
            {'id': 7233514,
             'membership_level_id': 12180,
             'status': 'active',
             'expire_date': '2024-09-15'},
            {'id': 7768155,
             'membership_level_id': 16738,
             'status': 'active',
             'expire_date': '2200-01-01'}
        ]
    }

    update_response = {
        'id': 14842209,
        'full_name': full_name,
        'email': email,
        'sign_in_count': 2,
        'current_sign_in_at': '2022-12-21T11:32:28.633-03:00',
        'profile_image_url': 'https://images.memberkit.com.br/',
        'created_at': '2022-12-19T11:46:18.864-03:00',
        'updated_at': '2023-03-24T11:28:18.351-03:00',
        'bio': '',
        'unlimited': False,
        'blocked': False,
        'metadata': {},
        'enrollments': [],
        'memberships': [
            {'id': 7768186,
             'membership_level_id': 4420,
             'status': 'expired',
             'expire_date': '2023-03-24'},
            {'id': 7768133,
             'membership_level_id': 11610,
             'status': 'expired',
             'expire_date': '0121-02-21'},
            {'id': 7233514,
             'membership_level_id': 12180,
             'status': 'active',
             'expire_date': '2024-09-15'},
            {'id': 7768155,
             'membership_level_id': 16738,
             'status': 'active',
             'expire_date': '2023-03-24'}]}
    status = 'active'
    update_json_params = {
        'full_name': full_name,
        'email': email,
        'status': status,
        'blocked': False,
        'membership_level_id': subscription_id,
        'unlimited': False,
        'expires_at': '24/03/2023',
    }
    responses.add(
        responses.GET,
        f'https://memberkit.com.br/api/v1/users/{memberkit_user_id}?api_key={api_key}',
        json=user_json_resp,
        status=200
    )
    responses.add(
        responses.POST,
        f'https://memberkit.com.br/api/v1/users?api_key={api_key}',
        json=update_response,
        status=204,
        match=[matchers.json_params_matcher(update_json_params)]
    )

    assert update_response == api.update_user_subscription(
        memberkit_user_id, subscription_id, status, date(2023, 3, 24)
    )


@pytest.mark.withoutresponses
def test_update_user_subscription_user_not_found(responses, api_key):
    memberkit_user_id = 148422093
    json_resp = {'error': 'Not Found'}
    responses.add(
        responses.GET,
        f'https://memberkit.com.br/api/v1/users/{memberkit_user_id}?api_key={api_key}',
        json=json_resp,
        status=404
    )
    with pytest.raises(HTTPError):
        api.update_user_subscription(memberkit_user_id, 1, 'active', date(2023, 3, 24))


def test_update_user_subscription_invalid_status(api_key):
    invalid_state = 'invalid'
    with pytest.raises(ValueError):
        api.update_user_subscription(1, 2, invalid_state, date(2023, 3, 24))
