from django import template


def duration(value):
    try:
        duration = int(value)
    except ValueError:
        return ''
    else:
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            output = f'{hours:02d} hora(s) {minutes:02d} minuto(s)s {seconds:02d} segundo(s)'
        else:
            output = f'{minutes:02d} minuto(s)s {seconds:02d} segundo(s)'
        return output


register = template.Library()
register.filter('duration', duration)
