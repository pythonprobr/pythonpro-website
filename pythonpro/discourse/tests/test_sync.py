import pytest
import responses

import pythonpro.domain.user_domain
from pythonpro.discourse import facade
from pythonpro.domain import user_domain


@pytest.fixture
def no_responses():
    with responses.RequestsMock() as r:
        yield r


def test_missing_discourse_api_key(settings, no_responses):
    settings.DISCOURSE_API_KEY = ''
    settings.DISCOURSE_BASE_URL = 'https://forum.python.pro.br/'
    with pytest.raises(facade.MissingDiscourseAPICredentials):
        pythonpro.domain.user_domain.sync_user_on_discourse(None)


def test_missing_discourse_api_user(settings, no_responses):
    settings.DISCOURSE_API_USER = ''
    settings.DISCOURSE_BASE_URL = 'https://forum.python.pro.br/'
    with pytest.raises(facade.MissingDiscourseAPICredentials):
        pythonpro.domain.user_domain.sync_user_on_discourse(None)


def test_no_integration_on_missing_url_config(settings, no_responses):
    settings.DISCOURSE_API_USER = ''
    settings.DISCOURSE_API_KEY = ''
    settings.DISCOURSE_BASE_URL = ''
    assert pythonpro.domain.user_domain.sync_user_on_discourse(None) is None


@pytest.fixture
def resps(settings):
    settings.DISCOURSE_API_USER = 'someuser'
    settings.DISCOURSE_API_KEY = 'some-key'
    settings.DISCOURSE_BASE_URL = 'https://forum.python.pro.br/'
    with responses.RequestsMock() as r:
        url = f'{settings.DISCOURSE_BASE_URL}/admin/users/sync_sso'
        r.add(r.POST, url=url, json=success_response)
        yield r


def test_user_sync(logged_user, resps, mocker):
    generate_mock = mocker.spy(user_domain, 'generate_sso_payload_and_signature')
    pythonpro.domain.user_domain.sync_user_on_discourse(logged_user, 'fellow', 'member')
    generate_mock.assert_called_once_with({
        'email': logged_user.email,
        'name': logged_user.first_name,
        'external_id': logged_user.id,
        'require_activation': 'false',
        'groups': 'fellow,member'
    })


success_response = {
    'id': 251,
    'username': 'renzo',
    'name': 'Renzo',
    'avatar_template': 'https://avatars.discourse.org/v4/letter/v/6789/{size}.png',
    'active': True,
    'admin': False,
    'moderator': False,
    'last_seen_at': '2019-04-05T12:52:17.378Z',
    'last_emailed_at': '2020-02-10T23:59:32.498Z',
    'created_at': '2019-03-16T19:13:19.428Z',
    'last_seen_age': 27154630.87707741,
    'last_emailed_age': 244195.756963475,
    'created_at_age': 28859768.82766433,
    'username_lower': 'renzo',
    'trust_level': 1,
    'manual_locked_trust_level': None,
    'flag_level': 0,
    'title': None,
    'time_read': 0,
    'staged': False,
    'days_visited': 11,
    'posts_read_count': 0,
    'topics_entered': 1,
    'post_count': 0,
    'can_send_activation_email': True,
    'can_activate': False,
    'can_deactivate': True,
    'ip_address': None,
    'registration_ip_address': None,
    'can_grant_admin': True,
    'can_revoke_admin': False,
    'can_grant_moderation': True,
    'can_revoke_moderation': False,
    'can_impersonate': True,
    'like_count': 0,
    'like_given_count': 0,
    'topic_count': 0,
    'flags_given_count': 0,
    'flags_received_count': 0,
    'private_topics_count': 1,
    'can_delete_all_posts': True,
    'can_be_deleted': True,
    'can_be_anonymized': True,
    'full_suspend_reason': None,
    'silence_reason': None,
    'primary_group_id': None,
    'badge_count': 1,
    'warnings_received_count': 0,
    'bounce_score': 0.0,
    'reset_bounce_score_after': None,
    'can_view_action_logs': True,
    'can_disable_second_factor': True,
    'api_key_count': 0,
    'akismet_state': None,
    'single_sign_on_record': {
        'user_id': 251,
        'external_id': '219',
        'last_payload': 'email=foo%40example.com&external_id=219&groups=&require_activation=false',
        'created_at': '2019-03-16T19:13:19.507Z',
        'updated_at': '2020-02-13T19:49:28.247Z',
        'external_username': None,
        'external_email': 'foo@example.com',
        'external_name': None,
        'external_avatar_url': None,
        'external_profile_background_url': None,
        'external_card_background_url': None
    },
    'approved_by': None,
    'suspended_by': None,
    'silenced_by': None,
    'groups': [{
        'id': 10,
        'automatic': True,
        'name': 'nivel_de_confianca_0',
        'display_name': 'nivel_de_confianca_0',
        'user_count': 8514,
        'mentionable_level': 0,
        'messageable_level': 0,
        'visibility_level': 1,
        'automatic_membership_email_domains': None,
        'automatic_membership_retroactive': False,
        'primary_group': False,
        'title': None,
        'grant_trust_level': None,
        'incoming_email': None,
        'has_messages': False,
        'flair_url': None,
        'flair_bg_color': None,
        'flair_color': None,
        'bio_raw': None,
        'bio_cooked': None,
        'bio_excerpt': None,
        'public_admission': False,
        'public_exit': False,
        'allow_membership_requests': False,
        'full_name': None,
        'default_notification_level': 3,
        'membership_request_template': None,
        'members_visibility_level': 0,
        'can_see_members': True,
        'publish_read_state': False
    },
        {
            'id': 11,
            'automatic': True,
            'name': 'nivel_de_confianca_1',
            'display_name': 'nivel_de_confianca_1',
            'user_count': 8494,
            'mentionable_level': 0,
            'messageable_level': 0,
            'visibility_level': 1,
            'automatic_membership_email_domains': None,
            'automatic_membership_retroactive': False,
            'primary_group': False,
            'title': None,
            'grant_trust_level': None,
            'incoming_email': None,
            'has_messages': False,
            'flair_url': None,
            'flair_bg_color': None,
            'flair_color': None,
            'bio_raw': None,
            'bio_cooked': None,
            'bio_excerpt': None,
            'public_admission': False,
            'public_exit': False,
            'allow_membership_requests': False,
            'full_name': None,
            'default_notification_level': 3,
            'membership_request_template': None,
            'members_visibility_level': 0,
            'can_see_members': True,
            'publish_read_state': False
        }]
}
