from itertools import permutations

import pytest
from activecampaign.exception import ActiveCampaignError

from pythonpro.email_marketing import facade


@pytest.fixture(autouse=True)
def contacts_mock(mocker):
    mock = mocker.patch('pythonpro.email_marketing.facade._client')
    return mock.contacts


@pytest.fixture
def find_active_campaign_contact_id_mock(mocker):
    mock = mocker.patch('pythonpro.email_marketing.facade._find_active_campaign_contact_id')
    mock.side_effect = lambda i: i
    return mock


@pytest.fixture
def find_active_campaign_absent_contact_mock(mocker):
    mock = mocker.patch('pythonpro.email_marketing.facade._find_active_campaign_contact_id')
    mock.side_effect = ActiveCampaignError
    return mock


def test_error_when_using_not_existing_role(contacts_mock):
    with pytest.raises(ValueError):
        facade.grant_role('foo@bar.com', 1, 'not-existing')
    assert contacts_mock.add_tag.called is False
    assert contacts_mock.remove_tag.called is False


def test_data_scientist_add_tag_existing_user(contacts_mock, find_active_campaign_contact_id_mock):
    facade.grant_role('foo@bar.com', 1, 'data-scientist')
    contacts_mock.add_tag.assert_called_once_with({'tags[1]': 'Data-scientist', 'id': 1})


def test_data_scientist_add_tag_absent_user(contacts_mock, find_active_campaign_absent_contact_mock):
    facade.grant_role('foo@bar.com', 1, 'data-scientist')
    contacts_mock.add_tag.assert_called_once_with({'tags[1]': 'Data-scientist', 'email': 'foo@bar.com'})


python_pro_roles = pytest.mark.parametrize(
    'granted_role, removed_roles',
    [
        ('lead', {'Client', 'Webdev', 'Member'}),
        ('client', {'Lead', 'Webdev', 'Member'}),
        ('webdev', {'Lead', 'Client', 'Member'}),
        ('member', {'Lead', 'Client', 'Webdev'}),
    ]
)


@python_pro_roles
def test_grant_python_pro_role_add_tag_existing_user(
        granted_role, removed_roles, contacts_mock, find_active_campaign_contact_id_mock):
    facade.grant_role('foo@bar.com', 2, granted_role)
    contacts_mock.add_tag.assert_called_once_with({'tags[1]': granted_role.capitalize(), 'id': 2})


@python_pro_roles
def test_grant_python_pro_role_remove_tag_absent_user(
        granted_role, removed_roles, contacts_mock, find_active_campaign_absent_contact_mock):
    facade.grant_role('user@email.com', 3, granted_role)
    # Must remove other roles in any order
    for removed_roles_permutation in permutations(removed_roles):
        dct = facade._build_tags_array(removed_roles_permutation)
        dct['email'] = 'user@email.com'
        try:
            contacts_mock.remove_tag.assert_called_once_with(dct)
        except AssertionError:
            pass
        else:
            return
    pytest.fail(f'Should call remove tags with {removed_roles}')
