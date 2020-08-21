from datetime import datetime

from django.utils import timezone

from pythonpro.launch.facade import (
    get_launch_status,
    get_opened_cpls,
    LAUNCH_STATUS_CPL1,
    LAUNCH_STATUS_CPL2,
    LAUNCH_STATUS_CPL3,
    LAUNCH_STATUS_CPL4,
    LAUNCH_STATUS_PPL,
    LAUNCH_STATUS_OPEN_CART,
    LAUNCH_STATUS_CLOSED
)


def test_should_return_launch_status_ppl_before_monday(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 9, 23, 59, 59))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_PPL


def test_should_return_launch_status_cpl1_on_mon_early(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 10))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_CPL1


def test_should_return_launch_status_cpl1_on_mon_late(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 10, 23, 59, 59))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_CPL1


def test_should_return_launch_status_cpl2_on_tue_early(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 11))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_CPL1


def test_should_return_launch_status_cpl2_on_tue_late(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 11, 23, 59, 59))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_CPL2


def test_should_return_launch_status_cpl3_on_wed_early(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 12))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_CPL2


def test_should_return_launch_status_cpl3_on_wed_late(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 12, 23, 59, 59))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_CPL3


def test_should_return_launch_status_cpl4_on_thu_early(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 13))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_CPL3


def test_should_return_launch_status_open_cart_on_first_day(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 16, 20))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_OPEN_CART


def test_should_return_launch_status_open_cart_on_last_day(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 19, 16, 59, 59))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_OPEN_CART


def test_should_return_launch_status_closed_on_day_after_closed(mocker):
    fake_today = timezone.make_aware(datetime(2020, 8, 19, 17))
    mocker.patch('pythonpro.launch.facade.timezone.now', return_value=fake_today)
    assert get_launch_status() == LAUNCH_STATUS_CLOSED


def test_should_return_only_cpl1(mocker):
    mocker.patch('pythonpro.launch.facade.get_launch_status', return_value=LAUNCH_STATUS_CPL1)
    assert get_opened_cpls() == ['cpl1']


def test_should_return_cpl1_to_2(mocker):
    mocker.patch('pythonpro.launch.facade.get_launch_status', return_value=LAUNCH_STATUS_CPL2)
    assert get_opened_cpls() == ['cpl1', 'cpl2']


def test_should_return_cpl1_to_3(mocker):
    mocker.patch('pythonpro.launch.facade.get_launch_status', return_value=LAUNCH_STATUS_CPL3)
    assert get_opened_cpls() == ['cpl1', 'cpl2', 'cpl3']


def test_should_return_cpl1_to_4(mocker):
    mocker.patch('pythonpro.launch.facade.get_launch_status', return_value=LAUNCH_STATUS_CPL4)
    assert get_opened_cpls() == ['cpl1', 'cpl2', 'cpl3', 'cpl4']
