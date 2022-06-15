from random import randint

import pytest
import responses
from activecampaign.client import Client

from pythonpro.email_marketing import facade
from pythonpro.email_marketing.facade import _normalise_id

API_URL = 'https://foo.pythonhosted.com'


@pytest.fixture
def setup_active_settings():
    client = facade._client
    facade._client = Client(API_URL, 'some key')
    # https://medium.com/@rishabhsrao/testing-lru-cache-functions-in-python-with-pytest-33dd5757d11c
    facade._get_lists.cache_clear()
    yield facade._client
    facade._client = client


@pytest.fixture
def resps(setup_active_settings):
    with responses.RequestsMock() as r:
        r.add(
            r.GET,
            'https://foo.pythonhosted.com/admin/api.php?api_action=list_list&api_key=some+key&api_output=json&ids=all',
            json=_lists,
            status=200
        )
        yield r


def test_lists(resps):
    lists = facade._get_lists()
    assert lists == {
        'Dev Pro': '1', 'Python Birds': '2', 'Pytools': '3', 'Prospects': '4', 'Plantão de Dúvidas': '5',
        'Usuários Ativos': '12'
    }


@pytest.fixture
def grant_role_mock(mocker):
    return mocker.patch('pythonpro.email_marketing.facade.grant_role')


@pytest.fixture
def resps_user_not_found(setup_active_settings):
    with responses.RequestsMock() as r:
        r.add(
            r.GET,
            'https://foo.pythonhosted.com/admin/api.php?api_action=list_list&api_key=some+key&api_output=json&ids=all',
            json=_lists, status=200
        )

        r.add(
            r.GET,
            (
                'https://foo.pythonhosted.com/admin/api.php?api_action=contact_list&api_key=some+key&api_output='
                'json&filters%5Bfields%5D%5B%25PYTHONPRO_ID%25%5D=0000000001&full=0'
            ),
            json=_user_not_found, status=200
        )
        r.add(
            r.POST,
            (
                'https://foo.pythonhosted.com/admin/api.php?api_action=contact_sync&'
                'api_key=some+key&api_output=json'
            ),
            json=_user_editon_ok, status=200
        )
        r.add(
            r.POST,
            (
                'https://foo.pythonhosted.com/api/3/contactLists'
            ),
            json=_user_editon_ok, status=200
        )

        yield r


def test_client_creation_user_not_found(resps_user_not_found, grant_role_mock):
    facade.create_or_update_client('Renzo Nuccitelli', 'renzo@python.pro.br', 'turma', id=1)
    body_payload = (
        'email=renzo%40python.pro.br&first_name=Renzo&tags=turma&p%5B4%5D=4&status=1'
        '&field%5B%25PYTHONPRO_ID%25%5D=0000000001'
    )
    assert resps_user_not_found.calls[2].request.body == body_payload


def test_lead_creation_user_not_found(resps_user_not_found, grant_role_mock):
    facade.create_or_update_lead('Renzo Nuccitelli', 'renzo@python.pro.br', 'turma', id=1)
    grant_role_mock.assert_called_once_with('renzo@python.pro.br', '0000000001', 'lead')


def test_member_creation_user_not_found(resps_user_not_found, grant_role_mock):
    facade.create_or_update_member('Renzo Nuccitelli', 'renzo@python.pro.br', 'turma', id=1)
    grant_role_mock.assert_called_once_with('renzo@python.pro.br', '0000000001', 'member')


def test_prospect_creation_user_not_found(resps_user_not_found, grant_role_mock):
    facade.create_or_update_with_no_role('Renzo Nuccitelli', 'renzo@python.pro.br', 'turma', id=1)
    assert grant_role_mock.called is False


@pytest.fixture
def resps_user_found(setup_active_settings):
    with responses.RequestsMock() as r:
        r.add(
            r.GET,
            'https://foo.pythonhosted.com/admin/api.php?api_action=list_list&api_key=some+key&api_output=json&ids=all',
            json=_lists, status=200
        )
        r.add(
            r.GET,
            (
                'https://foo.pythonhosted.com/admin/api.php?api_action=contact_list&api_key=some+key&api_output='
                'json&filters%5Bfields%5D%5B%25PYTHONPRO_ID%25%5D=0000000001&full=0'
            ),
            json=_user_found_by_id, status=200
        )
        r.add(
            r.POST,
            (
                'https://foo.pythonhosted.com/admin/api.php?api_action=contact_edit&api_key=some+key&api_output=json'
            ),
            json=_user_editon_ok, status=200
        )
        r.add(
            r.POST,
            (
                'https://foo.pythonhosted.com/api/3/contactLists'
            ),
            json=_user_editon_ok, status=200
        )

        yield r


def test_client_creation_user_found(resps_user_found, grant_role_mock):
    facade.create_or_update_client('Renzo Nuccitelli', 'renzo@python.pro.br', 'turma', id=1)
    body_payload = (
        'email=renzo%40python.pro.br&first_name=Renzo&tags=turma&p%5B4%5D=4&status=1'
        '&field%5B%25PYTHONPRO_ID%25%5D=0000000001&id=1'
    )
    assert resps_user_found.calls[2].request.body == body_payload


@pytest.fixture
def resps_two_users_found(setup_active_settings):
    with responses.RequestsMock() as r:
        r.add(
            r.GET,
            'https://foo.pythonhosted.com/admin/api.php?api_action=list_list&api_key=some+key&api_output=json&ids=all',
            json=_lists, status=200
        )
        r.add(
            r.GET,
            (
                'https://foo.pythonhosted.com/admin/api.php?api_action=contact_list&api_key=some+key&api_output='
                'json&filters%5Bfields%5D%5B%25PYTHONPRO_ID%25%5D=0000000001&full=0'
            ),
            json=_two_users_found_by_id, status=200
        )
        r.add(
            r.POST,
            (
                'https://foo.pythonhosted.com/admin/api.php?api_action=contact_sync&'
                'api_key=some+key&api_output=json'
            ),
            json=_user_editon_ok, status=200
        )
        r.add(
            r.POST,
            (
                'https://foo.pythonhosted.com/api/3/contactLists'
            ),
            json=_user_editon_ok, status=200
        )

        yield r


def test_client_creation_two_users_found(resps_two_users_found, grant_role_mock):
    facade.create_or_update_client('Renzo Nuccitelli', 'renzo@python.pro.br', 'turma', id=1)
    body_payload = (
        'email=renzo%40python.pro.br&first_name=Renzo&tags=turma&p%5B4%5D=4&status=1'
        '&field%5B%25PYTHONPRO_ID%25%5D=0000000001'
    )
    assert resps_two_users_found.calls[2].request.body == body_payload


@pytest.mark.parametrize('transform', [int, str])
def test_normalise_id(transform):
    id = randint(1, 1000000000)
    normalized_id = _normalise_id(transform(id))
    assert len(normalized_id) == 10
    assert int(normalized_id) == id


def test_normalise_id_none():
    normalized_id = _normalise_id(None)
    assert len(normalized_id) == 10
    assert int(normalized_id) == 0


def test_granted_client_role(resps_user_found, grant_role_mock):
    facade.create_or_update_client('Renzo Nuccitelli', 'renzo@python.pro.br', 'turma', id=1)
    grant_role_mock.assert_called_once_with('renzo@python.pro.br', '0000000001', 'client')


_user_editon_ok = {
    'subscriber_id': 1, 'sendlast_should': 0, 'sendlast_did': 0, 'result_code': 1,
    'result_message': 'Contato atualizado', 'result_output': 'json'
}

_user_not_found_data = {
    'email': 'renzo@python.pro.br',
    'first_name': 'Renzo',
    'tags': 'turma',
    'field[%PYTHONPRO_ID%]': '1',
    'p[4]': '4',
    'status': '1'
}

_user_found_by_id = {
    '0': {
        'id': '1', 'subscriberid': '1', 'cdate': '2019-11-28 10:06:18', 'sdate': '2019-12-11 15:09:13',
        'first_name': 'renzo', 'last_name': 'Nuccitelli', 'email': 'renzo@python.pro.br', 'last_list': 'Prospects',
        'avatar_url': 'foo'
    }, 'result_code': 1, 'result_message': 'Sucesso:algo retornou', 'result_output': 'json'
}

_two_users_found_by_id = {
    '0': {
        'id': '1', 'subscriberid': '1', 'cdate': '2019-11-28 10:06:18', 'sdate': '2019-12-11 15:09:13',
        'first_name': 'renzo', 'last_name': 'Nuccitelli', 'email': 'renzo@python.pro.br', 'last_list': 'Prospects',
        'avatar_url': 'foo'
    },
    '1': {
        'id': '2', 'subscriberid': '2', 'cdate': '2019-11-28 10:06:18', 'sdate': '2019-12-11 15:09:13',
        'first_name': 'Foo', 'last_name': 'Bar', 'email': 'bar@python.pro.br', 'last_list': 'Prospects',
        'avatar_url': 'foo'
    },
    'result_code': 1, 'result_message': 'Sucesso:algo retornou', 'result_output': 'json'
}

_user_not_found = {
    'result_code': 0, 'result_message': 'Falhou: não se obteu qualquer resultado', 'result_output': 'json'
}

_lists = {
    '0': {
        'id': '1', 'name': 'Dev Pro', 'cdate': '2019-11-28 10:06:18', 'private': '0', 'userid': '1',
        'subscriber_count': 1
    },
    '1': {
        'id': '2', 'name': 'Python Birds', 'cdate': '2019-12-06 12:25:21', 'private': '0', 'userid': '1',
        'subscriber_count': 0
    },
    '2': {
        'id': '3', 'name': 'Pytools', 'cdate': '2019-12-06 12:28:43', 'private': '0', 'userid': '1',
        'subscriber_count': 0
    }, '3': {
        'id': '4', 'name': 'Prospects', 'cdate': '2019-12-06 12:29:29', 'private': '0', 'userid': '1',
        'subscriber_count': 0
    },
    '4': {
        'id': '5', 'name': 'Plantão de Dúvidas', 'cdate': '2019-12-06 15:28:51', 'private': '0', 'userid': '1',
        'subscriber_count': 0
    },
    '5': {
        'id': '12', 'name': 'Usuários Ativos', 'cdate': '2020-06-06 15:28:51', 'private': '0', 'userid': '1',
        'subscriber_count': 0
    },
    'result_code': 1,
    'result_message': 'Sucesso:algo retornou',
    'result_output': 'json'
}
