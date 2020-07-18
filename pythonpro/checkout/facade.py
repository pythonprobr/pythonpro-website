from datetime import datetime

from django.utils import timezone

discount_50_percent_datetime_limit = timezone.make_aware(datetime(2020, 7, 18, 23, 59, 59))
launch_datetime_finish = timezone.make_aware(datetime(2020, 7, 19, 23, 59, 59))
launch_datetime_begin = timezone.make_aware(datetime(2020, 7, 16, 20, 0, 0))


def is_launch_open():
    return launch_datetime_begin <= timezone.now() <= launch_datetime_finish


def has_50_percent_discount():
    return is_launch_open() and (timezone.now() < discount_50_percent_datetime_limit)
