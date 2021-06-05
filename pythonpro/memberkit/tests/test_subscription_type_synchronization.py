import pytest

from pythonpro.memberkit import api, facade


@pytest.fixture
def api_key():
    key = 'some_key'
    api.set_default_api_key(key)
    return key


def test_api_not_called(settings):
    """
    Since pytest-responses check all request's calls, if one is made, this test will fail
    :return:
    """
    settings.MEMBERKIT_ON = False
    assert [] == api.list_membership_levels()


def test_syncronize_memberkit_subscriptions(responses, api_key, settings):
    settings.MEMBERKIT_ON = True
    api_response = [
        {
            'classroom_ids': [39668, 39731, 40566],
            'id': 13, 'name': 'Clientes', 'trial_period': 0},
        {
            'classroom_ids': [40531, 40532, 40533, 40534, 40535, 39668, 39731, 40566],
            'id': 14,
            'name': 'Bootcampers', 'trial_period': 0},
        {
            'classroom_ids': [40531, 40532, 40533, 40534, 40535, 39668, 39731, 40566],
            'id': 15, 'name': 'Membros',
            'trial_period': 0},
        {
            'classroom_ids': [40531, 40532, 39731, 40566],
            'id': 16, 'name': 'Webdevs', 'trial_period': 0},
        {
            'classroom_ids': [39668, 39731, 40566],
            'id': 17, 'name': 'Clientes', 'trial_period': 0},
        {
            'classroom_ids': [40531, 40532, 40533, 40534, 40535, 39668, 39731, 40566],
            'id': 18,
            'name': 'Bootcampers', 'trial_period': 0},
        {
            'classroom_ids': [40531, 40532, 40533, 40534, 40535, 39668, 39731, 40566],
            'id': 19,
            'name': 'Membros', 'trial_period': 0},
        {
            'classroom_ids': [40531, 40532, 39731, 40566],
            'id': 20,
            'name': 'Webdevs', 'trial_period': 0
        }
    ]
    id_name_dct = {d['id']: d['name'] for d in api_response}
    responses.add(
        responses.GET,
        f'https://memberkit.com.br/api/v1/membership_levels?api_key={api_key}',
        json=api_response
    )
    subscription_types = facade.synchronize_subscription_types()

    assert id_name_dct == {s.id: s.name for s in subscription_types}
