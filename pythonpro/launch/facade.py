from datetime import datetime, timedelta

from django.utils import timezone

LAUNCH_PPL_START_DATE = datetime(2020, 7, 20, 0)
LAUNCH_STATUS_PPL = 0
LAUNCH_STATUS_CPL1 = 1
LAUNCH_STATUS_CPL2 = 2
LAUNCH_STATUS_CPL3 = 3
LAUNCH_STATUS_CPL4 = 4
LAUNCH_STATUS_OPEN_CART = 5
LAUNCH_STATUS_CLOSED = -1


def _get_first_class_start():
    start_date = timezone.make_aware(LAUNCH_PPL_START_DATE)
    return start_date + timedelta(days=21)


def _get_second_class_start():
    return _get_first_class_start() + timedelta(days=1) + timedelta(hours=20)


def _get_third_class_start():
    return _get_second_class_start() + timedelta(days=1)


def _get_fourth_class_start():
    return _get_third_class_start() + timedelta(days=1)


def _get_open_cart_start():
    return _get_first_class_start() + timedelta(days=6) + timedelta(hours=19, minutes=59)


def _get_open_cart_end():
    return _get_first_class_start() + timedelta(days=9, hours=17)


def get_launch_status():
    if timezone.now() < _get_first_class_start():
        return LAUNCH_STATUS_PPL

    elif _get_first_class_start() <= timezone.now() < _get_second_class_start():
        return LAUNCH_STATUS_CPL1

    elif _get_second_class_start() <= timezone.now() < _get_third_class_start():
        return LAUNCH_STATUS_CPL2

    elif _get_third_class_start() <= timezone.now() < _get_fourth_class_start():
        return LAUNCH_STATUS_CPL3

    elif _get_fourth_class_start() <= timezone.now() < _get_open_cart_start():
        return LAUNCH_STATUS_CPL4

    elif _get_open_cart_start() <= timezone.now() < _get_open_cart_end():
        return LAUNCH_STATUS_OPEN_CART

    return LAUNCH_STATUS_CLOSED


def get_opened_cpls():
    output = []
    if get_launch_status() >= LAUNCH_STATUS_CPL1:
        output.append('cpl1')

    if get_launch_status() >= LAUNCH_STATUS_CPL2:
        output.append('cpl2')

    if get_launch_status() >= LAUNCH_STATUS_CPL3:
        output.append('cpl3')

    if get_launch_status() >= LAUNCH_STATUS_CPL4:
        output.append('cpl4')

    return output
