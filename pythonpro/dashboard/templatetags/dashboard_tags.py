from django import template


def duration(value):
    try:
        duration = int(value)
    except ValueError:
        return ''
    else:
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}'


register = template.Library()
register.filter('duration', duration)
