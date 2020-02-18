from datetime import datetime

import pytest
import pytz
from django.utils import timezone
from freezegun import freeze_time

from pythonpro.payments.facade import (
    PYTOOLS_DO_PRICE, PYTOOLS_OTO_PRICE, PYTOOLS_PRICE, PYTOOLS_PROMOTION_PRICE, _discover_pytools_price,
    calculate_oto_expires_datetime, calculate_pytools_promotion_interval, is_on_pytools_oto_season,
    is_on_pytools_promotion_season,
)


@pytest.mark.parametrize(
    'now', ['2019-07-{}'.format(day) for day in range(22, 29)]
)
def test_promotion_interval(now):
    with freeze_time(now):
        begin, end = datetime(2019, 7, 22, 0, 0, 0, tzinfo=pytz.utc), datetime(2019, 7, 27, 23, 59, 59, tzinfo=pytz.utc)
        assert (begin, end) == calculate_pytools_promotion_interval()


@pytest.mark.parametrize(
    'creation', [datetime(2019, 6, day, tzinfo=pytz.utc) for day in range(3, 10)]  # 7 weeks before now
)
def test_in_promotion_period(creation: datetime):
    with freeze_time('2019-07-22'):
        assert is_on_pytools_promotion_season(creation)


@pytest.mark.parametrize(
    'creation', [datetime(2019, 6, day, tzinfo=pytz.utc) for day in range(1, 2)]  # 8 weeks before now
)
def test_before_promotion_period(creation: datetime):
    with freeze_time('2019-07-22'):
        assert not is_on_pytools_promotion_season(creation)


@pytest.mark.parametrize(
    'creation', [datetime(2019, 6, day, tzinfo=pytz.utc) for day in range(10, 20)]  # 6 weeks before now
)
def test_after_promotion_period(creation: datetime):
    with freeze_time('2019-07-22'):
        assert not is_on_pytools_promotion_season(creation)


@pytest.fixture
def user_creation():
    return timezone.make_aware(datetime(2020, 1, 28, 16, 0, 0))


def test_should_calculate_oto_expires_datetime(user_creation):
    generated_date = timezone.make_aware(datetime(2020, 1, 28, 16, 30, 0))
    assert calculate_oto_expires_datetime(user_creation) == generated_date


def test_should_check_if_user_is_on_pytools_oto_season_and_return_true(mocker, user_creation):
    mocker.patch(
        'pythonpro.payments.facade.now',
        return_value=timezone.make_aware(datetime(2020, 1, 28, 16, 29, 59))
    )
    assert is_on_pytools_oto_season(user_creation) is True


def test_should_check_if_user_is_on_pytools_oto_season_and_return_false(mocker, user_creation):
    mocker.patch(
        'pythonpro.payments.facade.now',
        return_value=timezone.make_aware(datetime(2020, 1, 28, 16, 30))
    )
    assert is_on_pytools_oto_season(user_creation) is False


def test_should_discover_pytools_oto_price(mocker, user_creation):
    mocker.patch('pythonpro.payments.facade.is_on_pytools_oto_season', return_value=True)
    assert _discover_pytools_price(user_creation) == PYTOOLS_OTO_PRICE


def test_should_discover_pytools_do_price():
    assert _discover_pytools_price(datetime.now(), 'pytools-do') == PYTOOLS_DO_PRICE


def test_should_discover_pytools_promotion_price(mocker, user_creation):
    mocker.patch('pythonpro.payments.facade.is_on_pytools_oto_season', return_value=False)
    mocker.patch('pythonpro.payments.facade.is_on_pytools_promotion_season', return_value=True)
    assert _discover_pytools_price(user_creation) == PYTOOLS_PROMOTION_PRICE


def test_should_discover_pytools_regular_price(mocker, user_creation):
    mocker.patch('pythonpro.payments.facade.is_on_pytools_oto_season', return_value=False)
    mocker.patch('pythonpro.payments.facade.is_on_pytools_promotion_season', return_value=False)
    assert _discover_pytools_price(user_creation) == PYTOOLS_PRICE
