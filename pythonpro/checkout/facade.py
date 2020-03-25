from datetime import datetime

from django.utils import timezone

discount_datetime_limit = timezone.make_aware(datetime(2020, 4, 17, 12, 0, 0))
launch_datetime_finish = timezone.make_aware(datetime(2020, 4, 21, 23, 59, 59))
launch_datetime_begin = timezone.make_aware(datetime(2020, 4, 16, 20, 00, 00))


def is_launch_open():
    return launch_datetime_begin <= timezone.now() <= launch_datetime_finish


def is_launch_first_day_discount():
    return is_launch_open() and timezone.now() < discount_datetime_limit
