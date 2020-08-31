from datetime import datetime

from django.utils import timezone

launch_datetime_begin = timezone.make_aware(datetime(2020, 8, 16, 19, 0, 0))
discount_50_percent_datetime_limit = timezone.make_aware(datetime(2020, 8, 17, 23, 59, 59))
discount_35_percent_datetime_limit = timezone.make_aware(datetime(2020, 8, 18, 23, 59, 59))
launch_datetime_finish = timezone.make_aware(datetime(2020, 8, 31, 23, 59, 59))


def is_launch_open():
    return launch_datetime_begin <= timezone.now() <= launch_datetime_finish


def has_50_percent_discount():
    return is_launch_open() and (timezone.now() <= discount_50_percent_datetime_limit)


def has_35_percent_discount():
    return is_launch_open() and (
                discount_50_percent_datetime_limit < timezone.now() <= discount_35_percent_datetime_limit
    )
