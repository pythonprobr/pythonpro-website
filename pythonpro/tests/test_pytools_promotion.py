from datetime import datetime

import pytz
from freezegun import freeze_time
from model_mommy import mommy
from rolepermissions.roles import assign_role

from pythonpro import facade


def test_leads_in_promotion_period(db, django_user_model, mocker):
    dts = (datetime(2019, 6, day, tzinfo=pytz.utc) for day in range(3, 10))
    tag_as_mock = mocker.patch('pythonpro.facade._mailchimp_facade.tag_as')
    users_created_seven_weeks_ago = [mommy.make(django_user_model, date_joined=d) for d in dts]
    for user in users_created_seven_weeks_ago:
        assign_role(user, 'lead')
    with freeze_time('2019-07-22'):
        assert len(users_created_seven_weeks_ago) == facade.run_pytools_promotion_campaign()
    for user in users_created_seven_weeks_ago:
        tag_as_mock.assert_any_call(user.email, 'pytools-promotion')


def test_clients_not_marked_in_promotion_period(db, django_user_model, mocker):
    dts = (datetime(2019, 6, day, tzinfo=pytz.utc) for day in range(3, 10))
    tag_as_mock = mocker.patch('pythonpro.facade._mailchimp_facade.tag_as')
    users_created_seven_weeks_ago = [mommy.make(django_user_model, date_joined=d) for d in dts]
    for user in users_created_seven_weeks_ago:
        assign_role(user, 'client')
    with freeze_time('2019-07-22'):
        assert 0 == facade.run_pytools_promotion_campaign()
    assert tag_as_mock.call_count == 0


def test_members_not_marked_in_promotion_period(db, django_user_model, mocker):
    dts = (datetime(2019, 6, day, tzinfo=pytz.utc) for day in range(3, 10))
    tag_as_mock = mocker.patch('pythonpro.facade._mailchimp_facade.tag_as')
    users_created_seven_weeks_ago = [mommy.make(django_user_model, date_joined=d) for d in dts]
    for user in users_created_seven_weeks_ago:
        assign_role(user, 'client')
    with freeze_time('2019-07-22'):
        assert 0 == facade.run_pytools_promotion_campaign()
    assert tag_as_mock.call_count == 0


def test_before_promotion_period(db, django_user_model, mocker):
    dts = (datetime(2019, 6, day, tzinfo=pytz.utc) for day in range(1, 3))
    tag_as_mock = mocker.patch('pythonpro.facade._mailchimp_facade.tag_as')
    for d in dts:
        mommy.make(django_user_model, date_joined=d)
    with freeze_time('2019-07-22'):
        assert 0 == facade.run_pytools_promotion_campaign()
    assert tag_as_mock.call_count == 0


def test_after_promotion_period(db, django_user_model, mocker):
    dts = (datetime(2019, 6, day, tzinfo=pytz.utc) for day in range(10, 13))
    tag_as_mock = mocker.patch('pythonpro.facade._mailchimp_facade.tag_as')
    for d in dts:
        mommy.make(django_user_model, date_joined=d)
    with freeze_time('2019-07-22'):
        assert 0 == facade.run_pytools_promotion_campaign()
    assert tag_as_mock.call_count == 0
