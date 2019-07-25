from datetime import datetime

import pytest
import pytz
from freezegun import freeze_time

from pythonpro.payments.facade import calculate_pytools_promotion_interval, is_on_pytools_promotion_season


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
